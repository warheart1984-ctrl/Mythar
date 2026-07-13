from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .core import ULXGovernanceStore, discover_repo_root, governance_error
from .dsl import GovernanceDSLParseError, load_governance_dsl


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _repo_root_from_args(args: argparse.Namespace) -> Path:
    if getattr(args, "repo_root", ""):
        return Path(args.repo_root).expanduser().resolve()
    return discover_repo_root()


def _store(args: argparse.Namespace) -> ULXGovernanceStore:
    return ULXGovernanceStore(_repo_root_from_args(args))


def _emit_error(payload: dict[str, Any], exit_code: int = 1) -> int:
    _print_json(payload)
    return exit_code


def _chain_validate(args: argparse.Namespace) -> int:
    report = _store(args).chain_validation_report(args.substrate)
    _print_json(report)
    return 0 if report.get("ok") else 1


def _evidence_show(args: argparse.Namespace) -> int:
    report = _store(args).evidence_summary(args.substrate, raw=bool(args.raw))
    _print_json(report)
    return 0 if report.get("ok") else 1


def _authority_show(args: argparse.Namespace) -> int:
    report = _store(args).authority_summary(args.substrate)
    _print_json(report)
    return 0 if report.get("ok") else 1


def _continuity_timeline(args: argparse.Namespace) -> int:
    report = _store(args).continuity_timeline(args.substrate)
    _print_json(report)
    return 0 if report.get("ok") else 1


def _decision_log(args: argparse.Namespace) -> int:
    report = _store(args).decision_log(args.substrate)
    _print_json(report)
    return 0 if report.get("ok") else 1


def _promote(args: argparse.Namespace) -> int:
    store = _store(args)
    report = store.promote(
        args.substrate,
        args.to,
        conformance_path=Path(args.conformance).expanduser().resolve() if args.conformance else None,
        apply=not bool(args.dry_run),
        source="cli",
    )
    _print_json(report)
    return 0 if report.get("allowed") else 1


def _gov_apply(args: argparse.Namespace) -> int:
    store = _store(args)
    try:
        spec = load_governance_dsl(Path(args.file).expanduser().resolve())
    except GovernanceDSLParseError as exc:
        error = governance_error(
            error_type="runtime-invariant-violation",
            severity="error",
            decision_id="gov-apply:parse",
            substrate_id="unknown",
            code="RUNTIME_INVARIANT_BREACH",
            message=str(exc),
            details={"path": str(Path(args.file).expanduser().resolve())},
        )
        return _emit_error(error)

    if spec.action.lower() != "promote":
        error = governance_error(
            error_type="promotion-contract-violation",
            severity="error",
            decision_id=spec.decision_id,
            substrate_id=spec.substrate_id,
            code="PROMOTION_CONTRACT_UNMET",
            message=f"Unsupported governance action: {spec.action!r}",
            details=spec.to_dict(),
        )
        return _emit_error(error)

    result = store.submit_decision(
        spec.substrate_id,
        {
            "decision_id": spec.decision_id,
            "action": spec.action,
            "target": spec.target,
            "reason": spec.reason,
            "requires": list(spec.requires),
            "effects": list(spec.effects),
        },
        conformance_path=Path(args.conformance).expanduser().resolve() if args.conformance else None,
        source="dsl",
    )
    _print_json(
        {
            "ok": result.get("result") == "approved",
            "decision": spec.to_dict(),
            "result": result,
        }
    )
    return 0 if result.get("result") == "approved" else 1


def _daemon(args: argparse.Namespace) -> int:
    from .daemon import serve

    serve(
        repo_root=_repo_root_from_args(args),
        host=args.host,
        port=args.port,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ulx", description="ULX constitutional CLI")
    parser.add_argument("--repo-root", default="", help="ULX repository root (defaults to discovery).")
    sub = parser.add_subparsers(dest="cmd")

    chain = sub.add_parser("chain-validate", help="Validate CIEMS chain for a substrate.")
    chain.add_argument("substrate")
    chain.set_defaults(func=_chain_validate)

    evidence = sub.add_parser("evidence", help="Inspect evidence for a substrate.")
    evidence_sub = evidence.add_subparsers(dest="evidence_cmd", required=True)
    evidence_show = evidence_sub.add_parser("show", help="Show substrate evidence.")
    evidence_show.add_argument("substrate")
    evidence_show.add_argument("--raw", action="store_true", help="Emit raw evidence JSON.")
    evidence_show.set_defaults(func=_evidence_show)

    promote = sub.add_parser("promote", help="Request a substrate promotion decision.")
    promote.add_argument("substrate")
    promote.add_argument("--to", required=True)
    promote.add_argument("--conformance", default="", help="Optional conformance JSON path.")
    promote.add_argument("--dry-run", action="store_true", help="Evaluate without applying.")
    promote.set_defaults(func=_promote)

    authority = sub.add_parser("authority", help="Inspect authority metadata.")
    authority_sub = authority.add_subparsers(dest="authority_cmd", required=True)
    authority_show = authority_sub.add_parser("show", help="Show authority for a substrate.")
    authority_show.add_argument("substrate")
    authority_show.set_defaults(func=_authority_show)

    continuity = sub.add_parser("continuity", help="Inspect continuity history.")
    continuity_sub = continuity.add_subparsers(dest="continuity_cmd", required=True)
    continuity_timeline = continuity_sub.add_parser("timeline", help="Show substrate continuity timeline.")
    continuity_timeline.add_argument("substrate")
    continuity_timeline.set_defaults(func=_continuity_timeline)

    decision = sub.add_parser("decision", help="Inspect constitutional decisions.")
    decision_sub = decision.add_subparsers(dest="decision_cmd", required=True)
    decision_log = decision_sub.add_parser("log", help="Show governance decision log.")
    decision_log.add_argument("substrate")
    decision_log.set_defaults(func=_decision_log)

    gov = sub.add_parser("gov", help="Apply a governance DSL program.")
    gov_sub = gov.add_subparsers(dest="gov_cmd", required=True)
    gov_apply = gov_sub.add_parser("apply", help="Apply a governance DSL file.")
    gov_apply.add_argument("file")
    gov_apply.add_argument("--conformance", default="", help="Optional conformance JSON path.")
    gov_apply.set_defaults(func=_gov_apply)

    daemon = sub.add_parser("daemon", help="Run the ULX daemon.")
    daemon.add_argument("--host", default="127.0.0.1")
    daemon.add_argument("--port", type=int, default=8799)
    daemon.set_defaults(func=_daemon)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return int(args.func(args))

