#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SubstrateSpec:
    id: str
    name: str
    source: str
    domain: str = "general"
    layer: str = "general"
    status: str = "normalized"
    owner: str = "jon"
    promotion: str = "requires-evidence"
    branch: str = ""


@dataclass(frozen=True)
class MigrationPlanEntry:
    id: str
    source: str
    normalized_dir: str
    raw_dir: str
    mode: str
    branch: str


@dataclass(frozen=True)
class MigrationResult:
    substrate_id: str
    source: str
    normalized_dir: str
    raw_dir: str
    evidence_bundle: str
    substrate_contract: str
    merge_mode: str
    merge_commit: str
    status: str


def canonical_project_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise MigrationError("project id cannot be empty after normalization")
    if not PROJECT_ID_PATTERN.fullmatch(slug):
        raise MigrationError(f"invalid project id: {value!r}")
    return slug


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "Codex")
    env.setdefault("GIT_AUTHOR_EMAIL", "codex@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Codex")
    env.setdefault("GIT_COMMITTER_EMAIL", "codex@example.com")
    return env


def _run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=_git_env(),
    )
    if check and result.returncode != 0:
        raise MigrationError(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip() or result.stdout.strip()}"
        )
    return result


def _is_git_repo(path: Path) -> bool:
    if not path.exists():
        return False
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    return Path(result.stdout.strip()).resolve() == path.resolve()


def _current_branch(path: Path) -> str:
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
    branch = result.stdout.strip()
    return branch if branch and branch != "HEAD" else "main"


def _filter_repo_available() -> bool:
    result = subprocess.run(
        ["git", "filter-repo", "--help"],
        capture_output=True,
        text=True,
    )
    return result.returncode in {0, 129} or "filter-repo" not in result.stderr.lower()


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MigrationError("manifest must be a JSON object")
    substrates = data.get("substrates")
    if not isinstance(substrates, list) or not substrates:
        raise MigrationError("manifest must contain a non-empty substrates array")
    return data


def _parse_substrates(manifest: dict[str, Any]) -> list[SubstrateSpec]:
    specs: list[SubstrateSpec] = []
    for raw in manifest["substrates"]:
        if not isinstance(raw, dict):
            raise MigrationError("each substrate entry must be an object")
        source = str(raw.get("source", "")).strip()
        if not source:
            raise MigrationError("each substrate requires a source")
        substrate_id = canonical_project_id(str(raw.get("id", "")).strip())
        name = str(raw.get("name", "")).strip() or substrate_id.replace("-", " ").title()
        spec = SubstrateSpec(
            id=substrate_id,
            name=name,
            source=source,
            domain=canonical_project_id(str(raw.get("domain", "general")).strip()) if str(raw.get("domain", "general")).strip() else "general",
            layer=str(raw.get("layer", "general")).strip() or "general",
            status=str(raw.get("status", "normalized")).strip() or "normalized",
            owner=str(raw.get("owner", "jon")).strip() or "jon",
            promotion=str(raw.get("promotion", "requires-evidence")).strip() or "requires-evidence",
            branch=str(raw.get("branch", "")).strip(),
        )
        specs.append(spec)
    return specs


def build_migration_plan(manifest_path: Path, target_repo: Path, workspace: Path) -> list[MigrationPlanEntry]:
    manifest = _load_manifest(manifest_path)
    specs = _parse_substrates(manifest)
    mode = "filter-repo" if _filter_repo_available() else "subtree"
    plan: list[MigrationPlanEntry] = []
    for spec in specs:
        normalized_dir = target_repo / "substrates" / spec.id
        raw_dir = workspace / "raw" / spec.id
        plan.append(
            MigrationPlanEntry(
                id=spec.id,
                source=spec.source,
                normalized_dir=str(normalized_dir),
                raw_dir=str(raw_dir),
                mode=mode,
                branch=spec.branch,
            )
        )
    return plan


def _ensure_repo(path: Path) -> None:
    if _is_git_repo(path):
        return
    path.mkdir(parents=True, exist_ok=True)
    _run_git(["init"], path)
    _run_git(["checkout", "-B", "main"], path)


def _clone_source(spec: SubstrateSpec, raw_dir: Path) -> Path:
    raw_dir.parent.mkdir(parents=True, exist_ok=True)
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    clone_args = ["clone", "--no-single-branch"]
    if spec.branch:
        clone_args.extend(["--branch", spec.branch])
    clone_args.extend([spec.source, str(raw_dir)])
    _run_git(clone_args, Path.cwd())
    return raw_dir


def _normalize_with_filter_repo(source_dir: Path, substrate_id: str) -> Path:
    if shutil.which("git-filter-repo") is None and _filter_repo_available() is False:
        raise MigrationError("git-filter-repo is not available")
    _run_git(["filter-repo", "--force", "--to-subdirectory-filter", f"substrates/{substrate_id}"], source_dir)
    return source_dir


def _subtree_add(target_repo: Path, source_dir: Path, substrate_id: str, branch: str, merge_message: str) -> str:
    branch_ref = branch or _current_branch(source_dir)
    _run_git(["subtree", "add", f"--prefix=substrates/{substrate_id}", str(source_dir), branch_ref, "-m", merge_message], target_repo)
    head = _run_git(["rev-parse", "HEAD"], target_repo).stdout.strip()
    return head


def _merge_normalized_repo(target_repo: Path, normalized_dir: Path, substrate_id: str, merge_message: str) -> str:
    remote_name = f"substrate-{substrate_id}"
    branch = _current_branch(normalized_dir)
    _run_git(["remote", "add", remote_name, str(normalized_dir)], target_repo)
    try:
        _run_git(["fetch", remote_name, branch], target_repo)
        _run_git(
            ["merge", "--allow-unrelated-histories", "--no-ff", "FETCH_HEAD", "-m", merge_message],
            target_repo,
        )
    finally:
        _run_git(["remote", "remove", remote_name], target_repo, check=False)
    return _run_git(["rev-parse", "HEAD"], target_repo).stdout.strip()


def _git_list(path: Path, args: list[str]) -> list[str]:
    result = _run_git(args, path)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _ensure_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def _posix_path(path: Path) -> str:
    return path.as_posix()


def _substrate_record_paths(substrate_id: str) -> dict[str, Path]:
    root = Path("constitutional")
    return {
        "intent": root / "ilc" / f"{substrate_id}.intent.json",
        "evidence": root / "provenance" / f"{substrate_id}.evidence.json",
        "authority": root / "cic" / f"{substrate_id}.authority.json",
        "continuity": root / "ccc" / f"{substrate_id}.continuity.json",
        "conformance": root / "provenance" / f"{substrate_id}.conformance.json",
        "decision": root / "provenance" / f"{substrate_id}.promotion.json",
    }


def _ensure_substrate_scaffold(normalized_dir: Path) -> None:
    _ensure_text_file(normalized_dir / "docs" / "README.md", "# Substrate Documentation\n")
    _ensure_text_file(normalized_dir / "docs" / "architecture.md", "# Architecture\n")
    _ensure_text_file(normalized_dir / "docs" / "governance.md", "# Governance\n")
    _ensure_text_file(normalized_dir / "tests" / "README.md", "# Tests\n")
    _ensure_text_file(
        normalized_dir / "build" / "ulx.build.json",
        json.dumps(
            {
                "system": "custom",
                "entry": "build/ulx.build.json",
                "artifacts_dir": "dist",
                "requires": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def build_evidence_bundle(
    substrate: SubstrateSpec,
    raw_dir: Path,
    target_repo: Path,
    normalized_dir: Path,
    merge_mode: str,
    merge_commit: str,
    record_paths: dict[str, Path],
) -> dict[str, Any]:
    commit_hashes = _git_list(raw_dir, ["rev-list", "--reverse", "--all"])
    authors = _git_list(raw_dir, ["shortlog", "-sne", "--all"])
    tags = _git_list(raw_dir, ["tag", "--list"])
    head = _run_git(["rev-parse", "HEAD"], raw_dir).stdout.strip()
    root_commit = commit_hashes[0] if commit_hashes else head
    branch = _current_branch(raw_dir)
    evidence = {
        "schema": "ulx.substrate.evidence.v1",
        "generatedAt": _timestamp(),
        "substrate": {
            "id": substrate.id,
            "domain": substrate.domain,
            "layer": substrate.layer,
            "status": substrate.status,
        },
        "origin": {
            "source": substrate.source,
            "branch": branch,
            "rawDir": str(raw_dir),
        },
        "target": {
            "repo": str(target_repo),
            "normalizedDir": str(normalized_dir),
            "mergeMode": merge_mode,
            "mergeCommit": merge_commit,
        },
        "ciems": {
            "intent": {"record": _posix_path(record_paths["intent"])},
            "evidence": {"record": _posix_path(record_paths["evidence"])},
            "authority": {"record": _posix_path(record_paths["authority"])},
            "continuity": {"record": _posix_path(record_paths["continuity"])},
        },
        "lineage": {
            "head": head,
            "rootCommit": root_commit,
            "commitCount": len(commit_hashes),
            "tags": tags,
            "authors": authors,
        },
        "contracts": {
            "identity": True,
            "build": True,
            "tests": True,
            "docs": True,
            "governance": True,
        },
        "replayRequirements": [
            "temporal-lineage",
            "merge-decision",
            "evidence-bundle",
        ],
        "conformanceRequirements": [
            "substrate.json",
            "build entry",
            "tests",
            "docs",
            "governance metadata",
        ],
    }
    return evidence


def build_substrate_contract(
    substrate: SubstrateSpec,
    raw_dir: Path,
    merge_commit: str,
    merge_mode: str,
    record_paths: dict[str, Path],
) -> dict[str, Any]:
    commit_hashes = _git_list(raw_dir, ["rev-list", "--reverse", "--all"])
    tags = _git_list(raw_dir, ["tag", "--list"])
    import_commit = commit_hashes[-1] if commit_hashes else merge_commit
    return {
        "$schema": "https://ulx/constitutional/substrate.schema.json",
        "id": substrate.id,
        "name": substrate.name,
        "domain": substrate.domain,
        "layer": substrate.layer,
        "status": "normalized",
        "lineage": {
            "origin_repo": substrate.source,
            "origin_path": f"substrates/{substrate.id}-raw",
            "import_commit": import_commit,
            "normalized_from": f"{substrate.id}-raw",
            "tags": tags,
        },
        "build": {
            "system": "custom",
            "entry": "build/ulx.build.json",
            "artifacts_dir": "dist",
            "requires": [],
        },
        "tests": {
            "framework": "custom",
            "entry": "tests",
            "min_coverage": 0.7,
        },
        "docs": {
            "readme": "docs/README.md",
            "architecture": "docs/architecture.md",
            "governance": "docs/governance.md",
        },
        "governance": {
            "owner": substrate.owner,
            "status": "normalized",
            "promotion": substrate.promotion,
            "stewards": [substrate.owner],
            "promotion_policy": "ciems-standard",
            "risk_level": "medium",
        },
        "ciems": {
            "intent": {"record": _posix_path(record_paths["intent"])},
            "evidence": {"record": _posix_path(record_paths["evidence"])},
            "authority": {"record": _posix_path(record_paths["authority"])},
            "continuity": {"record": _posix_path(record_paths["continuity"])},
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_substrate_contract(normalized_dir: Path, payload: dict[str, Any]) -> Path:
    contract_path = normalized_dir / "substrate.json"
    _write_json(contract_path, payload)
    return contract_path


def _write_evidence_bundle(workspace: Path, substrate: SubstrateSpec, bundle: dict[str, Any]) -> Path:
    evidence_dir = workspace / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{substrate.id}.json"
    _write_json(evidence_path, bundle)
    return evidence_path


def _write_ciems_records(
    base_dir: Path,
    substrate: SubstrateSpec,
    evidence_bundle: dict[str, Any],
    merge_commit: str,
    merge_mode: str,
) -> dict[str, Path]:
    record_paths = _substrate_record_paths(substrate.id)
    intent_record = {
        "id": substrate.id,
        "source": substrate.source,
        "normalized_from": f"{substrate.id}-raw",
        "mergeMode": merge_mode,
        "mergeCommit": merge_commit,
        "status": "normalized",
    }
    authority_record = {
        "id": substrate.id,
        "owner": substrate.owner,
        "stewards": [substrate.owner],
        "promotion_policy": substrate.promotion,
        "risk_level": "medium",
    }
    continuity_record = {
        "id": substrate.id,
        "mergeCommit": merge_commit,
        "mergeMode": merge_mode,
        "replayRequirements": evidence_bundle.get("replayRequirements", []),
        "conformanceRequirements": evidence_bundle.get("conformanceRequirements", []),
    }
    _write_json(base_dir / record_paths["intent"], intent_record)
    _write_json(base_dir / record_paths["evidence"], evidence_bundle)
    _write_json(base_dir / record_paths["authority"], authority_record)
    _write_json(base_dir / record_paths["continuity"], continuity_record)
    return record_paths


def execute_migration(manifest_path: Path, target_repo: Path, workspace: Path, dry_run: bool = False) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    specs = _parse_substrates(manifest)
    _ensure_repo(target_repo)
    workspace.mkdir(parents=True, exist_ok=True)
    plan = build_migration_plan(manifest_path, target_repo, workspace)
    results: list[MigrationResult] = []
    mode = "filter-repo" if _filter_repo_available() else "subtree"

    if dry_run:
        return {
            "generatedAt": _timestamp(),
            "mode": mode,
            "plan": [asdict(entry) for entry in plan],
            "results": [],
        }

    for spec in specs:
        raw_dir = workspace / "raw" / spec.id
        normalized_dir = target_repo / "substrates" / spec.id
        used_mode = mode
        _clone_source(spec, raw_dir)
        _ensure_substrate_scaffold(raw_dir)
        record_paths = _substrate_record_paths(spec.id)
        canonical_bundle = build_evidence_bundle(spec, raw_dir, target_repo, normalized_dir, used_mode, "", record_paths)
        _write_ciems_records(raw_dir, spec, canonical_bundle, "", used_mode)
        contract = build_substrate_contract(spec, raw_dir, "", used_mode, record_paths)
        _write_json(raw_dir / "substrate.json", contract)
        _run_git(["add", "."], raw_dir)
        _run_git(["commit", "-m", f"norm({spec.id}): substrate scaffold and CIEMS records"], raw_dir)

        merge_commit = ""
        if mode == "filter-repo":
            normalized_clone = workspace / "normalized" / spec.id
            if normalized_clone.exists():
                shutil.rmtree(normalized_clone)
            shutil.copytree(raw_dir, normalized_clone)
            _normalize_with_filter_repo(normalized_clone, spec.id)
            _ensure_repo(target_repo)
            merge_message = f"norm({spec.id}): constitutional merge into ULX"
            merge_commit = _merge_normalized_repo(target_repo, normalized_clone, spec.id, merge_message)
        else:
            merge_message = f"norm({spec.id}): constitutional merge into ULX"
            merge_commit = _subtree_add(target_repo, raw_dir, spec.id, spec.branch, merge_message)

        bundle = build_evidence_bundle(spec, raw_dir, target_repo, normalized_dir, used_mode, merge_commit, record_paths)
        evidence_path = _write_evidence_bundle(workspace, spec, bundle)
        results.append(
            MigrationResult(
                substrate_id=spec.id,
                source=spec.source,
                normalized_dir=str(normalized_dir),
                raw_dir=str(raw_dir),
                evidence_bundle=str(evidence_path),
                substrate_contract=str(raw_dir / "substrate.json"),
                merge_mode=used_mode,
                merge_commit=merge_commit,
                status="promoted",
            )
        )

    report = {
        "generatedAt": _timestamp(),
        "targetRepo": str(target_repo),
        "mode": mode,
        "plan": [asdict(entry) for entry in plan],
        "results": [asdict(item) for item in results],
    }
    report_path = workspace / "migration-report.json"
    _write_json(report_path, report)
    report["reportPath"] = str(report_path)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize imported repositories into ULX substrates.")
    parser.add_argument("--manifest", required=True, help="Path to the substrate migration manifest JSON.")
    parser.add_argument("--target-repo", required=True, help="ULX target repository path.")
    parser.add_argument("--workspace", default="", help="Workspace directory for raw and normalized clones.")
    parser.add_argument("--dry-run", action="store_true", help="Plan the migration without applying it.")
    parser.add_argument("--plan-only", action="store_true", help="Emit the migration plan and exit.")
    parser.add_argument("--output", default="", help="Optional path for the JSON report or plan output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    manifest_path = Path(args.manifest).expanduser().resolve()
    target_repo = Path(args.target_repo).expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else target_repo / ".ulx-migration"

    plan = build_migration_plan(manifest_path, target_repo, workspace)
    if args.plan_only:
        payload = {
            "generatedAt": _timestamp(),
            "mode": "filter-repo" if _filter_repo_available() else "subtree",
            "plan": [asdict(entry) for entry in plan],
        }
        if args.output:
            _write_json(Path(args.output).expanduser().resolve(), payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    payload = execute_migration(manifest_path, target_repo, workspace, dry_run=bool(args.dry_run))
    if args.output:
        _write_json(Path(args.output).expanduser().resolve(), payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
