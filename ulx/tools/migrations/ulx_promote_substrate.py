#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS_VALUES = ("raw", "normalized", "experimental", "active", "stable", "deprecated")
DOMAIN_VALUES = ("core-os", "governance", "ide", "game", "ai", "utility", "prototype", "experiment", "archive")
LAYER_VALUES = ("intent", "evidence", "planning", "execution", "validation")


class PromotionError(RuntimeError):
    pass


@dataclass(frozen=True)
class PromotionDecision:
    substrate_id: str
    from_status: str
    to_status: str
    contract_id: str
    allowed: bool
    missing_requirements: list[str]
    substrate_path: str
    decision_path: str
    conformance_path: str
    checked_at: str


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
        raise PromotionError(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip() or result.stdout.strip()}"
        )
    return result


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PromotionError(f"{path} must contain a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True))
        handle.write("\n")


def _validate_substrate_record(record: dict[str, Any]) -> None:
    if not isinstance(record.get("id"), str) or not PROJECT_ID_PATTERN.fullmatch(record["id"]):
        raise PromotionError("substrate.json.id must be kebab-case")
    if record.get("domain") not in DOMAIN_VALUES:
        raise PromotionError("substrate.json.domain is not valid")
    if record.get("layer") not in LAYER_VALUES:
        raise PromotionError("substrate.json.layer is not valid")
    if record.get("status") not in STATUS_VALUES:
        raise PromotionError("substrate.json.status is not valid")
    for field in ("lineage", "build", "tests", "docs", "governance", "ciems"):
        if not isinstance(record.get(field), dict):
            raise PromotionError(f"substrate.json.{field} must be an object")


def _require_exists(base: Path, relative_path: str, label: str, missing: list[str]) -> None:
    if not relative_path:
        missing.append(label)
        return
    if not (base / relative_path).exists():
        missing.append(label)


def _load_conformance(conformance_path: Path | None) -> dict[str, Any]:
    if conformance_path is None or not conformance_path.exists():
        return {}
    return _load_json(conformance_path)


def _find_transition(contract: dict[str, Any], from_status: str, to_status: str) -> dict[str, Any] | None:
    for transition in contract.get("transitions", []):
        if isinstance(transition, dict) and transition.get("from") == from_status and transition.get("to") == to_status:
            return transition
    return None


def evaluate_promotion(
    repo_root: Path,
    substrate_id: str,
    to_status: str,
    conformance_path: Path | None = None,
    contract_path: Path | None = None,
) -> PromotionDecision:
    substrate_id = substrate_id.strip().lower()
    if not PROJECT_ID_PATTERN.fullmatch(substrate_id):
        raise PromotionError("substrate id must be kebab-case")
    if to_status not in STATUS_VALUES:
        raise PromotionError(f"invalid target status: {to_status}")

    substrate_path = repo_root / "substrates" / substrate_id / "substrate.json"
    if not substrate_path.exists():
        raise PromotionError(f"substrate not found: {substrate_path}")
    record = _load_json(substrate_path)
    _validate_substrate_record(record)
    from_status = str(record.get("status", "")).strip()
    substrate_dir = substrate_path.parent

    if contract_path is None:
        contract_path = repo_root / "constitutional" / "promotion" / "ciems-standard.json"
    contract = _load_json(contract_path)
    contract_id = str(contract.get("id", "ciems-standard"))
    transition = _find_transition(contract, from_status, to_status)
    if transition is None:
        raise PromotionError(f"no contract transition from {from_status!r} to {to_status!r}")

    conformance = _load_conformance(conformance_path)
    missing: list[str] = []

    lineage = record.get("lineage", {})
    build = record.get("build", {})
    tests = record.get("tests", {})
    docs = record.get("docs", {})
    governance = record.get("governance", {})
    ciems = record.get("ciems", {})

    requirements = [str(item) for item in transition.get("requires", []) if isinstance(item, str)]
    for requirement in requirements:
        if requirement == "substrate.json.exists":
            continue
        if requirement == "build.system.defined" and not str(build.get("system", "")).strip():
            missing.append(requirement)
        elif requirement == "docs.readme.exists":
            _require_exists(substrate_dir, str(docs.get("readme", "")), requirement, missing)
        elif requirement == "tests.entry.exists":
            _require_exists(substrate_dir, str(tests.get("entry", "")), requirement, missing)
        elif requirement == "ciems.intent.record.exists":
            _require_exists(substrate_dir, str(ciems.get("intent", {}).get("record", "")), requirement, missing)
        elif requirement == "ciems.evidence.record.exists":
            _require_exists(substrate_dir, str(ciems.get("evidence", {}).get("record", "")), requirement, missing)
        elif requirement == "tests.pass":
            if bool(conformance.get("tests", {}).get("pass")) is not True:
                missing.append(requirement)
        elif requirement == "coverage >= tests.min_coverage":
            minimum = float(tests.get("min_coverage", 0.0))
            coverage = float(conformance.get("tests", {}).get("coverage", -1.0))
            if coverage < minimum:
                missing.append(requirement)
        elif requirement == "governance.owner.set":
            if not str(governance.get("owner", "")).strip():
                missing.append(requirement)
        elif requirement == "governance.status == experimental":
            if str(governance.get("status", "")).strip() != "experimental":
                missing.append(requirement)
        elif requirement == "no_open_blocker_issues":
            if bool(conformance.get("replay", {}).get("no_open_blocker_issues", False)) is not True:
                missing.append(requirement)
        elif requirement == "no_failing_replay_jobs":
            if bool(conformance.get("replay", {}).get("no_failing_replay_jobs", False)) is not True:
                missing.append(requirement)
        elif requirement == "continuity.contract.valid":
            if bool(conformance.get("continuity", {}).get("contract_valid", False)) is not True:
                missing.append(requirement)
        elif requirement == "deprecation_notice.docs.exists":
            if not (substrate_dir / "docs" / "deprecation.md").exists():
                missing.append(requirement)
        elif requirement == "replacement.substrate.id.optional":
            continue
        else:
            if requirement.startswith("substrate.json"):
                continue
            missing.append(requirement)

    decision_path = repo_root / "constitutional" / "provenance" / f"{substrate_id}.promotion.json"
    conformance_output = conformance_path if conformance_path is not None else repo_root / "constitutional" / "provenance" / f"{substrate_id}.conformance.json"
    allowed = not missing
    return PromotionDecision(
        substrate_id=substrate_id,
        from_status=from_status,
        to_status=to_status,
        contract_id=contract_id,
        allowed=allowed,
        missing_requirements=missing,
        substrate_path=str(substrate_path),
        decision_path=str(decision_path),
        conformance_path=str(conformance_output),
        checked_at=_timestamp(),
    )


def promote_substrate(
    repo_root: Path,
    substrate_id: str,
    to_status: str,
    conformance_path: Path | None = None,
    apply: bool = True,
) -> dict[str, Any]:
    decision = evaluate_promotion(repo_root, substrate_id, to_status, conformance_path=conformance_path)
    report = asdict(decision)
    if not decision.allowed:
        report["status"] = "blocked"
        return report

    substrate_path = Path(decision.substrate_path)
    record = _load_json(substrate_path)
    record["status"] = to_status
    governance = record.get("governance", {})
    if isinstance(governance, dict):
        governance["status"] = to_status
        record["governance"] = governance
    if apply:
        _write_json(substrate_path, record)

    decision_record = {
        "$schema": "https://ulx/constitutional/promotion.schema.json",
        "substrate_id": decision.substrate_id,
        "from": decision.from_status,
        "to": decision.to_status,
        "contract_id": decision.contract_id,
        "allowed": decision.allowed,
        "missing_requirements": decision.missing_requirements,
        "substrate_path": decision.substrate_path,
        "conformance_path": decision.conformance_path,
        "checked_at": decision.checked_at,
        "applied": bool(apply),
    }
    _write_json(Path(decision.decision_path), decision_record)
    _append_jsonl(
        repo_root / "logs" / "governance" / f"{decision.substrate_id}.log.jsonl",
        {
            "type": "decision",
            "substrate_id": decision.substrate_id,
            "from": decision.from_status,
            "to": decision.to_status,
            "result": "approved" if decision.allowed else "blocked",
            "allowed": decision.allowed,
            "missing_requirements": decision.missing_requirements,
            "checked_at": decision.checked_at,
            "applied": bool(apply),
            "decision_path": decision.decision_path,
            "substrate_path": decision.substrate_path,
        },
    )
    if apply:
        _run_git(
            [
                "add",
                str(substrate_path.relative_to(repo_root)),
                str(Path(decision.decision_path).relative_to(repo_root)),
            ],
            repo_root,
        )
        _run_git(
            [
                "commit",
                "-m",
                f"promote({decision.substrate_id}): {decision.from_status} -> {decision.to_status}",
            ],
            repo_root,
        )
    report["status"] = "promoted"
    report["applied"] = bool(apply)
    report["substrate_record"] = decision.substrate_path
    report["decision_record"] = decision.decision_path
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote a ULX substrate through the CIEMS workflow.")
    parser.add_argument("--repo-root", required=True, help="ULX repository root.")
    parser.add_argument("--substrate-id", required=True, help="Substrate id in kebab-case.")
    parser.add_argument("--to", required=True, help="Target promotion state.")
    parser.add_argument("--conformance", default="", help="Optional conformance report JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate promotion without writing substrate.json.")
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    conformance_path = Path(args.conformance).expanduser().resolve() if args.conformance else None
    report = promote_substrate(repo_root, args.substrate_id, args.to, conformance_path=conformance_path, apply=not args.dry_run)
    if args.output:
        _write_json(Path(args.output).expanduser().resolve(), report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
