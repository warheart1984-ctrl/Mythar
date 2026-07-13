#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .ulx_normalize_substrates import canonical_project_id
except ImportError:  # pragma: no cover - script execution fallback
    from ulx_normalize_substrates import canonical_project_id


class CensusError(RuntimeError):
    pass


@dataclass(frozen=True)
class RepoCensusEntry:
    id: str
    name: str
    source: str
    git_root: str
    branch: str
    head: str
    commit_count: int
    tag_count: int
    tags: list[str]
    authors: list[str]
    domain: str
    layer: str
    status: str
    owner: str
    promotion: str
    queue_index: int
    pilot_bucket: str
    pilot_reason: str

    def as_manifest_entry(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update(
            {
                "source_kind": "git-worktree",
                "name": self.name,
                "source": self.source,
                "branch": self.branch,
                "status": self.status,
                "owner": self.owner,
                "promotion": self.promotion,
                "domain": self.domain,
                "layer": self.layer,
            }
        )
        return payload


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "Codex")
    env.setdefault("GIT_AUTHOR_EMAIL", "codex@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Codex")
    env.setdefault("GIT_COMMITTER_EMAIL", "codex@example.com")
    return env


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=_git_env(),
    )
    if result.returncode != 0:
        raise CensusError(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip() or result.stdout.strip()}"
        )
    return result


def _is_git_repo(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
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


def _git_list(path: Path, args: list[str]) -> list[str]:
    result = _run_git(args, path)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _normalise_repo_name(path: Path) -> str:
    return path.name.replace("_", " ").replace("-", " ").strip().title() or path.name


def _infer_domain(repo_name: str) -> str:
    lowered = repo_name.lower()
    if "os" in lowered or lowered.startswith("aaes"):
        return "core-os"
    if "agent" in lowered or "shell" in lowered or "console" in lowered:
        return "utility"
    if "skill" in lowered or "tool" in lowered:
        return "utility"
    if "infi" in lowered or "infinity" in lowered or "project" in lowered:
        return "prototype"
    return "experiment"


def _infer_layer(repo_name: str) -> str:
    lowered = repo_name.lower()
    if "docs" in lowered or "readme" in lowered:
        return "planning"
    if "agent" in lowered or "shell" in lowered or "console" in lowered:
        return "execution"
    return "execution"


def _candidate_roots(workspace_root: Path, include_paths: Iterable[Path]) -> list[Path]:
    roots: list[Path] = []
    if workspace_root.exists():
        for child in sorted(workspace_root.iterdir(), key=lambda path: path.name.lower()):
            if child.is_dir():
                roots.append(child)
    for path in include_paths:
        if path.exists():
            roots.append(path)
    ordered: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(resolved)
    return ordered


def discover_git_roots(
    workspace_root: Path,
    include_paths: Iterable[Path] | None = None,
    exclude_paths: Iterable[Path] | None = None,
) -> list[Path]:
    includes = list(include_paths or [])
    excludes = [path.resolve() for path in (exclude_paths or [])]
    discovered: list[Path] = []
    for root in _candidate_roots(workspace_root, includes):
        if any(root == excluded or excluded in root.parents for excluded in excludes):
            continue
        if _is_git_repo(root):
            discovered.append(root)
    return discovered


def _pilot_bucket(repo_name: str) -> tuple[str, str]:
    lowered = repo_name.lower()
    if "aaes" in lowered or lowered.endswith("-os") or lowered.endswith("os"):
        return "core-os", "core-operating-surface"
    if "agent" in lowered or "shell" in lowered or "console" in lowered:
        return "agentic", "agentic-control-surface"
    if "project" in lowered or "infi" in lowered or "infinity" in lowered:
        return "platform", "platform-runtime-surface"
    return "general", "general-surface"


def _repo_entry(path: Path, queue_index: int) -> RepoCensusEntry:
    repo_name = path.name
    canonical_id = canonical_project_id(repo_name)
    branch = _current_branch(path)
    head = _run_git(["rev-parse", "HEAD"], path).stdout.strip()
    commit_hashes = _git_list(path, ["rev-list", "--reverse", "--all"])
    tags = _git_list(path, ["tag", "--list"])
    authors = _git_list(path, ["shortlog", "-sne", "--all"])
    bucket, reason = _pilot_bucket(repo_name)
    return RepoCensusEntry(
        id=canonical_id,
        name=_normalise_repo_name(path),
        source=str(path),
        git_root=str(path),
        branch=branch,
        head=head,
        commit_count=len(commit_hashes),
        tag_count=len(tags),
        tags=tags,
        authors=authors,
        domain=_infer_domain(repo_name),
        layer=_infer_layer(repo_name),
        status="raw",
        owner="jon",
        promotion="requires-evidence",
        queue_index=queue_index,
        pilot_bucket=bucket,
        pilot_reason=reason,
    )


def _collision_entry(kind: str, substrate_id: str, message: str, sources: list[str]) -> dict[str, Any]:
    return {
        "kind": kind,
        "substrate_id": substrate_id,
        "message": message,
        "sources": sources,
    }


def detect_census_collisions(entries: list[RepoCensusEntry]) -> list[dict[str, Any]]:
    collisions: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}
    seen_sources: dict[str, str] = {}
    for entry in entries:
        if entry.id in seen_ids:
            collisions.append(
                _collision_entry(
                    "duplicate-id",
                    entry.id,
                    "more than one source normalizes to the same substrate id",
                    [seen_ids[entry.id], entry.source],
                )
            )
        else:
            seen_ids[entry.id] = entry.source
        if entry.source in seen_sources:
            collisions.append(
                _collision_entry(
                    "duplicate-source",
                    entry.id,
                    "the same source root was discovered more than once",
                    [seen_sources[entry.source], entry.source],
                )
            )
        else:
            seen_sources[entry.source] = entry.id
    ordered = sorted(entries, key=lambda item: (Path(item.source).resolve().as_posix().lower(), item.id))
    for left_index, left in enumerate(ordered):
        left_path = Path(left.source).resolve()
        for right in ordered[left_index + 1 :]:
            right_path = Path(right.source).resolve()
            if left_path == right_path:
                continue
            if left_path in right_path.parents or right_path in left_path.parents:
                collisions.append(
                    _collision_entry(
                        "nested-root",
                        left.id if len(left.source) <= len(right.source) else right.id,
                        "one source root is nested inside another source root",
                        [left.source, right.source],
                    )
                )
    return collisions


def select_pilot_entries(entries: list[RepoCensusEntry], limit: int = 3) -> list[RepoCensusEntry]:
    if limit <= 0:
        return []

    selected: list[RepoCensusEntry] = []
    selected_ids: set[str] = set()

    def pick_first(predicate) -> None:
        for entry in entries:
            if entry.id in selected_ids:
                continue
            if predicate(entry):
                selected.append(entry)
                selected_ids.add(entry.id)
                return

    pick_first(lambda entry: entry.pilot_bucket == "core-os")
    pick_first(lambda entry: entry.pilot_bucket == "agentic")
    pick_first(lambda entry: entry.pilot_bucket == "platform")

    if len(selected) < limit:
        for entry in sorted(entries, key=lambda item: (-item.commit_count, -item.tag_count, item.id)):
            if entry.id in selected_ids:
                continue
            selected.append(entry)
            selected_ids.add(entry.id)
            if len(selected) >= limit:
                break
    return selected[:limit]


def generate_repo_census(
    workspace_root: Path,
    include_paths: Iterable[Path] | None = None,
    exclude_paths: Iterable[Path] | None = None,
    pilot_limit: int = 3,
) -> dict[str, Any]:
    workspace_root = workspace_root.expanduser().resolve()
    include_paths = list(include_paths or [])
    exclude_paths = list(exclude_paths or [])
    roots = discover_git_roots(workspace_root, include_paths=include_paths, exclude_paths=exclude_paths)
    entries = [_repo_entry(path, index) for index, path in enumerate(sorted(roots, key=lambda item: item.as_posix().lower()))]
    collisions = detect_census_collisions(entries)
    pilot_entries = select_pilot_entries(entries, limit=pilot_limit)
    selected_ids = [entry.id for entry in pilot_entries]
    return {
        "$schema": "https://ulx/constitutional/repo-census.schema.json",
        "generatedAt": _timestamp(),
        "workspaceRoot": str(workspace_root),
        "scan": {
            "include": [str(path.expanduser().resolve()) for path in include_paths],
            "exclude": [str(path.expanduser().resolve()) for path in exclude_paths],
            "discoveredRoots": [str(path) for path in roots],
            "candidateCount": len(_candidate_roots(workspace_root, include_paths)),
            "repositoryCount": len(entries),
        },
        "inventory": {
            "repositoryCount": len(entries),
            "collisionCount": len(collisions),
            "pilotLimit": pilot_limit,
        },
        "substrates": [entry.as_manifest_entry() for entry in entries],
        "collisions": collisions,
        "pilot": {
            "limit": pilot_limit,
            "selected": selected_ids,
            "subsets": [entry.as_manifest_entry() for entry in pilot_entries],
        },
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> Path:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a deterministic ULX repo census manifest.")
    parser.add_argument("--workspace-root", required=True, help="Root directory to scan for git repositories.")
    parser.add_argument("--output", required=True, help="Path to write the census manifest JSON.")
    parser.add_argument("--include", action="append", default=[], help="Extra repository roots to include.")
    parser.add_argument("--exclude", action="append", default=[], help="Repository roots to exclude.")
    parser.add_argument("--pilot-limit", type=int, default=3, help="Number of pilot repositories to select.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    include_paths = [Path(item).expanduser().resolve() for item in args.include]
    exclude_paths = [Path(item).expanduser().resolve() for item in args.exclude]
    manifest = generate_repo_census(
        workspace_root,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        pilot_limit=args.pilot_limit,
    )
    write_manifest(Path(args.output), manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
