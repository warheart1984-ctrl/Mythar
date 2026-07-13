#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from . import ulx_normalize_substrates as normalizer
    from .ulx_repo_census import RepoCensusEntry, canonical_project_id
except ImportError:  # pragma: no cover - script execution fallback
    import ulx_normalize_substrates as normalizer
    from ulx_repo_census import RepoCensusEntry, canonical_project_id


class BatchMigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class BatchCollision:
    kind: str
    substrate_id: str
    message: str
    sources: list[str]


@dataclass(frozen=True)
class BatchReportEntry:
    substrate_id: str
    source: str
    normalized_dir: str
    status: str
    dry_run: bool
    collisions: list[dict[str, Any]]
    result: dict[str, Any] | None
    error: str | None
    report_path: str


def _timestamp() -> str:
    return normalizer._timestamp()  # type: ignore[attr-defined]


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BatchMigrationError("manifest must be a JSON object")
    if not isinstance(payload.get("substrates"), list):
        raise BatchMigrationError("manifest must contain a substrates array")
    return payload


def _load_entries(manifest: dict[str, Any]) -> list[RepoCensusEntry]:
    entries: list[RepoCensusEntry] = []
    for index, raw in enumerate(manifest.get("substrates", [])):
        if not isinstance(raw, dict):
            raise BatchMigrationError("each substrate entry must be an object")
        substrate_id = canonical_project_id(str(raw.get("id", "")).strip())
        source = str(raw.get("source", "")).strip()
        if not source:
            raise BatchMigrationError(f"substrate {substrate_id} is missing a source")
        entries.append(
            RepoCensusEntry(
                id=substrate_id,
                name=str(raw.get("name", substrate_id.replace("-", " ").title())).strip() or substrate_id,
                source=source,
                git_root=str(raw.get("git_root", source)).strip() or source,
                branch=str(raw.get("branch", "main")).strip() or "main",
                head=str(raw.get("head", "")).strip(),
                commit_count=int(raw.get("commit_count", 0) or 0),
                tag_count=int(raw.get("tag_count", 0) or 0),
                tags=[str(item) for item in raw.get("tags", []) if isinstance(item, str)],
                authors=[str(item) for item in raw.get("authors", []) if isinstance(item, str)],
                domain=str(raw.get("domain", "experiment")).strip() or "experiment",
                layer=str(raw.get("layer", "execution")).strip() or "execution",
                status=str(raw.get("status", "raw")).strip() or "raw",
                owner=str(raw.get("owner", "jon")).strip() or "jon",
                promotion=str(raw.get("promotion", "requires-evidence")).strip() or "requires-evidence",
                queue_index=index,
                pilot_bucket=str(raw.get("pilot_bucket", "general")).strip() or "general",
                pilot_reason=str(raw.get("pilot_reason", "general-surface")).strip() or "general-surface",
            )
        )
    return entries


def detect_collisions(entries: list[RepoCensusEntry], target_repo: Path) -> list[BatchCollision]:
    collisions: list[BatchCollision] = []
    seen_ids: dict[str, str] = {}
    seen_sources: dict[str, str] = {}
    seen_targets: dict[str, str] = {}
    target_resolved = target_repo.expanduser().resolve()

    for entry in entries:
        source_resolved = Path(entry.source).expanduser().resolve()
        normalized_dir = target_resolved / "substrates" / entry.id
        normalized_key = normalized_dir.as_posix().lower()

        if source_resolved == target_resolved:
            collisions.append(
                BatchCollision(
                    kind="target-self",
                    substrate_id=entry.id,
                    message="source root is the target ULX repository itself",
                    sources=[entry.source, str(target_resolved)],
                )
            )

        if entry.id in seen_ids:
            collisions.append(
                BatchCollision(
                    kind="duplicate-id",
                    substrate_id=entry.id,
                    message="more than one source normalizes to the same substrate id",
                    sources=[seen_ids[entry.id], entry.source],
                )
            )
        else:
            seen_ids[entry.id] = entry.source

        if entry.source in seen_sources:
            collisions.append(
                BatchCollision(
                    kind="duplicate-source",
                    substrate_id=entry.id,
                    message="the same source root was included more than once",
                    sources=[seen_sources[entry.source], entry.source],
                )
            )
        else:
            seen_sources[entry.source] = entry.id

        if normalized_key in seen_targets:
            collisions.append(
                BatchCollision(
                    kind="duplicate-target",
                    substrate_id=entry.id,
                    message="more than one substrate targets the same normalized path",
                    sources=[seen_targets[normalized_key], entry.source],
                )
            )
        else:
            seen_targets[normalized_key] = entry.source

    ordered = sorted(entries, key=lambda item: (Path(item.source).resolve().as_posix().lower(), item.id))
    for left_index, left in enumerate(ordered):
        left_path = Path(left.source).expanduser().resolve()
        for right in ordered[left_index + 1 :]:
            right_path = Path(right.source).expanduser().resolve()
            if left_path == right_path:
                continue
            if left_path in right_path.parents or right_path in left_path.parents:
                collisions.append(
                    BatchCollision(
                        kind="nested-source",
                        substrate_id=left.id if len(left.source) <= len(right.source) else right.id,
                        message="one source root is nested inside another source root",
                        sources=[left.source, right.source],
                    )
                )
    return collisions


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _manifest_subset(manifest: dict[str, Any], entries: list[RepoCensusEntry]) -> dict[str, Any]:
    payload = dict(manifest)
    payload["substrates"] = [
        {
            **asdict(entry),
            "source_kind": "git-worktree",
            "name": entry.name,
            "source": entry.source,
            "branch": entry.branch,
            "domain": entry.domain,
            "layer": entry.layer,
            "status": entry.status,
            "owner": entry.owner,
            "promotion": entry.promotion,
        }
        for entry in entries
    ]
    return payload


def _write_temporary_manifest(workspace: Path, substrate_id: str, payload: dict[str, Any]) -> Path:
    manifest_dir = workspace / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"{substrate_id}.manifest.json"
    _write_json(manifest_path, payload)
    return manifest_path


def _report_path(workspace: Path, substrate_id: str) -> Path:
    return workspace / "reports" / f"{substrate_id}.json"


def run_batch_migration(
    manifest_path: Path,
    target_repo: Path,
    workspace: Path,
    dry_run: bool = False,
    subset_ids: list[str] | None = None,
    pilot_only: bool = False,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    all_entries = _load_entries(manifest)
    if pilot_only:
        pilot_ids = [str(item) for item in manifest.get("pilot", {}).get("selected", []) if isinstance(item, str)]
        subset_ids = pilot_ids or subset_ids
    if subset_ids:
        wanted = {canonical_project_id(item) for item in subset_ids}
        entries = [entry for entry in all_entries if entry.id in wanted]
    else:
        entries = list(all_entries)

    workspace = workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    collisions = detect_collisions(entries, target_repo)
    collision_ids = {collision.substrate_id for collision in collisions}
    reports: list[BatchReportEntry] = []

    for entry in entries:
        entry_collisions = [asdict(collision) for collision in collisions if collision.substrate_id == entry.id]
        report_file = _report_path(workspace, entry.id)
        error_message: str | None = None
        result: dict[str, Any] | None = None
        status = "blocked" if entry.id in collision_ids else "planned"

        if not dry_run and entry.id not in collision_ids:
            try:
                subset_manifest = _manifest_subset(manifest, [entry])
                temp_manifest_path = _write_temporary_manifest(workspace, entry.id, subset_manifest)
                result = normalizer.execute_migration(
                    temp_manifest_path,
                    target_repo.expanduser().resolve(),
                    workspace / "runs" / entry.id,
                    dry_run=False,
                )
                status = "promoted"
            except Exception as exc:  # pragma: no cover - defensive surface for batch failures
                error_message = str(exc)
                status = "failed"
        elif dry_run and entry.id not in collision_ids:
            result = {
                "planned": True,
                "targetRepo": str(target_repo.expanduser().resolve()),
                "substrate": entry.id,
            }

        report = BatchReportEntry(
            substrate_id=entry.id,
            source=entry.source,
            normalized_dir=str(target_repo.expanduser().resolve() / "substrates" / entry.id),
            status=status,
            dry_run=dry_run,
            collisions=entry_collisions,
            result=result,
            error=error_message,
            report_path=str(report_file),
        )
        _write_json(report_file, asdict(report))
        reports.append(report)

    summary = {
        "generatedAt": _timestamp(),
        "targetRepo": str(target_repo.expanduser().resolve()),
        "workspace": str(workspace),
        "dryRun": dry_run,
        "pilotOnly": pilot_only,
        "subsetIds": [canonical_project_id(item) for item in subset_ids] if subset_ids else [],
        "collisions": [asdict(collision) for collision in collisions],
        "reports": [asdict(report) for report in reports],
        "resultCount": len(reports),
        "promotedCount": sum(1 for report in reports if report.status == "promoted"),
        "blockedCount": sum(1 for report in reports if report.status == "blocked"),
        "failedCount": sum(1 for report in reports if report.status == "failed"),
    }
    summary_path = workspace / "batch-report.json"
    _write_json(summary_path, summary)
    summary["reportPath"] = str(summary_path)
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ULX substrate migrations in batch.")
    parser.add_argument("--manifest", required=True, help="Census or migration manifest JSON.")
    parser.add_argument("--target-repo", required=True, help="ULX repository root.")
    parser.add_argument("--workspace", default="", help="Batch workspace for temporary manifests and reports.")
    parser.add_argument("--dry-run", action="store_true", help="Plan the batch without applying migrations.")
    parser.add_argument("--pilot-only", action="store_true", help="Use the pilot subset from the manifest.")
    parser.add_argument("--subset", action="append", default=[], help="Explicit substrate id to include.")
    parser.add_argument("--output", default="", help="Optional output path for the summary JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    manifest_path = Path(args.manifest).expanduser().resolve()
    target_repo = Path(args.target_repo).expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else target_repo / ".ulx-batch"
    summary = run_batch_migration(
        manifest_path,
        target_repo,
        workspace,
        dry_run=bool(args.dry_run),
        subset_ids=[str(item) for item in args.subset] if args.subset else None,
        pilot_only=bool(args.pilot_only),
    )
    if args.output:
        _write_json(Path(args.output).expanduser().resolve(), summary)
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
