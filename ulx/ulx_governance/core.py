from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from tools.migrations import ulx_promote_substrate as promoter

PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS_VALUES = ("raw", "normalized", "experimental", "active", "stable", "deprecated")
DOMAIN_VALUES = ("core-os", "governance", "ide", "game", "ai", "utility", "prototype", "experiment", "archive")
LAYER_VALUES = ("intent", "evidence", "planning", "execution", "validation")
PROMOTION_ORDER = ("raw", "normalized", "experimental", "active", "stable")

ERROR_CODE_BY_TYPE = {
    "chain-validation-failed": "CIEMS_CHAIN_MISSING",
    "evidence-missing": "EVIDENCE_NOT_FOUND",
    "authority-insufficient": "AUTHORITY_DENIED",
    "continuity-broken": "CONTINUITY_BREAK_UNRESOLVED",
    "promotion-contract-violation": "PROMOTION_CONTRACT_UNMET",
    "runtime-invariant-violation": "RUNTIME_INVARIANT_BREACH",
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        handle.write("\n")


def discover_repo_root(start: Path | None = None) -> Path:
    probe = (start or Path.cwd()).resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / "constitutional").exists() and (candidate / "tools").exists():
            return candidate
    return probe


def _sanitize_substrate_id(value: str) -> str:
    substrate_id = value.strip().lower()
    if not PROJECT_ID_PATTERN.fullmatch(substrate_id):
        raise ValueError(f"invalid substrate id: {value!r}")
    return substrate_id


@dataclass(frozen=True)
class ConstitutionalError:
    error_id: str
    type: str
    severity: str
    decision_id: str
    substrate_id: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_timestamp)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def governance_error(
    *,
    error_type: str,
    severity: str,
    decision_id: str,
    substrate_id: str,
    message: str,
    details: dict[str, Any] | None = None,
    code: str | None = None,
    error_id: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    payload = ConstitutionalError(
        error_id=error_id or f"err-{substrate_id}-{hashlib.sha256(_stable_json([decision_id, error_type, message]).encode('utf-8')).hexdigest()[:12]}",
        type=error_type,
        severity=severity,
        decision_id=decision_id,
        substrate_id=substrate_id,
        code=code or ERROR_CODE_BY_TYPE.get(error_type, "RUNTIME_INVARIANT_BREACH"),
        message=message,
        details=details or {},
        timestamp=timestamp or _timestamp(),
    )
    return payload.to_dict()


@dataclass(frozen=True)
class SubstratePaths:
    repo_root: Path
    substrate_id: str
    substrate_dir: Path
    substrate_record: Path
    intent_record: Path
    evidence_record: Path
    authority_record: Path
    continuity_record: Path
    provenance_dir: Path
    logs_dir: Path


def _substrate_paths(repo_root: Path, substrate_id: str) -> SubstratePaths:
    normalized_id = _sanitize_substrate_id(substrate_id)
    substrate_dir = repo_root / "substrates" / normalized_id
    provenance_dir = repo_root / "constitutional" / "provenance"
    return SubstratePaths(
        repo_root=repo_root,
        substrate_id=normalized_id,
        substrate_dir=substrate_dir,
        substrate_record=substrate_dir / "substrate.json",
        intent_record=repo_root / "constitutional" / "ilc" / f"{normalized_id}.intent.json",
        evidence_record=repo_root / "constitutional" / "provenance" / f"{normalized_id}.evidence.json",
        authority_record=repo_root / "constitutional" / "cic" / f"{normalized_id}.authority.json",
        continuity_record=repo_root / "constitutional" / "ccc" / f"{normalized_id}.continuity.json",
        provenance_dir=provenance_dir,
        logs_dir=repo_root / "logs",
    )


class ULXGovernanceStore:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = (repo_root or discover_repo_root()).resolve()

    def substrate_paths(self, substrate_id: str) -> SubstratePaths:
        return _substrate_paths(self.repo_root, substrate_id)

    def list_substrates(self) -> list[dict[str, Any]]:
        substrates_dir = self.repo_root / "substrates"
        if not substrates_dir.exists():
            return []
        items: list[dict[str, Any]] = []
        for substrate_dir in sorted(p for p in substrates_dir.iterdir() if p.is_dir()):
            substrate_record = substrate_dir / "substrate.json"
            if not substrate_record.exists():
                continue
            try:
                record = _read_json(substrate_record)
            except Exception:
                continue
            items.append(
                {
                    "id": record.get("id", substrate_dir.name),
                    "name": record.get("name", substrate_dir.name.replace("-", " ").title()),
                    "domain": record.get("domain", "unknown"),
                    "layer": record.get("layer", "unknown"),
                    "status": record.get("status", "unknown"),
                    "path": str(substrate_dir),
                }
            )
        return items

    def load_substrate_record(self, substrate_id: str) -> dict[str, Any]:
        paths = self.substrate_paths(substrate_id)
        if not paths.substrate_record.exists():
            raise FileNotFoundError(f"substrate record not found: {paths.substrate_record}")
        record = _read_json(paths.substrate_record)
        if str(record.get("id", "")).strip() != paths.substrate_id:
            raise ValueError(
                f"substrate id mismatch: expected {paths.substrate_id!r}, got {record.get('id')!r}"
            )
        return record

    def _record_payload(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return _read_json(path)

    def _chain_error(self, substrate_id: str, missing: list[str], mismatched: list[str], message: str) -> dict[str, Any]:
        return {
            "ok": False,
            "error": governance_error(
                error_type="chain-validation-failed",
                severity="error",
                decision_id=f"chain-validate:{substrate_id}",
                substrate_id=substrate_id,
                code="CIEMS_CHAIN_MISSING" if missing else "CIEMS_CHAIN_INCONSISTENT",
                message=message,
                details={
                    "missing": missing,
                    "mismatched": mismatched,
                },
            ),
        }

    def chain_validation_report(self, substrate_id: str) -> dict[str, Any]:
        normalized_id = _sanitize_substrate_id(substrate_id)
        paths = self.substrate_paths(normalized_id)
        missing: list[str] = []
        mismatched: list[str] = []
        if not paths.substrate_record.exists():
            missing.append("substrate.json")
            return self._chain_error(normalized_id, missing, mismatched, "substrate.json is missing")
        try:
            record = self.load_substrate_record(normalized_id)
        except Exception as exc:
            return self._chain_error(
                normalized_id,
                ["substrate.json"],
                mismatched,
                f"substrate.json failed validation: {exc}",
            )

        checks = {
            "substrate": paths.substrate_record.exists(),
            "intent": paths.intent_record.exists(),
            "evidence": paths.evidence_record.exists(),
            "authority": paths.authority_record.exists(),
            "continuity": paths.continuity_record.exists(),
            "docs_readme": (paths.substrate_dir / "docs" / "README.md").exists(),
            "docs_architecture": (paths.substrate_dir / "docs" / "architecture.md").exists(),
            "docs_governance": (paths.substrate_dir / "docs" / "governance.md").exists(),
            "build_entry": (paths.substrate_dir / "build" / "ulx.build.json").exists(),
            "tests_entry": (paths.substrate_dir / "tests").exists(),
        }
        for name, ok in checks.items():
            if not ok:
                missing.append(name)

        expected_ids = {
            "intent": paths.intent_record,
            "evidence": paths.evidence_record,
            "authority": paths.authority_record,
            "continuity": paths.continuity_record,
        }
        payloads: dict[str, dict[str, Any]] = {"substrate": record}
        for label, path in expected_ids.items():
            payload = self._record_payload(path)
            if payload is None:
                continue
            payloads[label] = payload
            if str(payload.get("id", "")).strip() not in {"", normalized_id}:
                mismatched.append(label)

        if missing or mismatched:
            return self._chain_error(
                normalized_id,
                missing,
                mismatched,
                "CIEMS chain is incomplete or inconsistent",
            )

        chain = {
            "substrate": record,
            "intent": payloads.get("intent", {}),
            "evidence": payloads.get("evidence", {}),
            "authority": payloads.get("authority", {}),
            "continuity": payloads.get("continuity", {}),
            "status": record.get("status", "unknown"),
        }
        summary = {
            "id": record.get("id", normalized_id),
            "name": record.get("name", normalized_id.replace("-", " ").title()),
            "domain": record.get("domain"),
            "layer": record.get("layer"),
            "status": record.get("status"),
            "lineage": record.get("lineage", {}),
        }
        return {
            "ok": True,
            "substrate_id": normalized_id,
            "validated_at": _timestamp(),
            "checks": checks,
            "chain": chain,
            "summary": summary,
        }

    def evidence_summary(self, substrate_id: str, raw: bool = False) -> dict[str, Any]:
        paths = self.substrate_paths(substrate_id)
        if not paths.evidence_record.exists():
            return {
                "ok": False,
                "error": governance_error(
                    error_type="evidence-missing",
                    severity="error",
                    decision_id=f"evidence-show:{paths.substrate_id}",
                    substrate_id=paths.substrate_id,
                    code="EVIDENCE_NOT_FOUND",
                    message=f"Evidence record {paths.evidence_record.name} is missing.",
                    details={"path": str(paths.evidence_record)},
                ),
            }
        payload = _read_json(paths.evidence_record)
        if raw:
            return {"ok": True, "substrate_id": paths.substrate_id, "evidence": payload}
        return {
            "ok": True,
            "substrate_id": paths.substrate_id,
            "summary": {
                "schema": payload.get("schema"),
                "generatedAt": payload.get("generatedAt"),
                "origin": payload.get("origin", {}),
                "target": payload.get("target", {}),
                "contracts": payload.get("contracts", {}),
                "replayRequirements": payload.get("replayRequirements", []),
            },
            "evidence": payload if raw else None,
        }

    def authority_summary(self, substrate_id: str) -> dict[str, Any]:
        paths = self.substrate_paths(substrate_id)
        if not paths.authority_record.exists():
            return {
                "ok": False,
                "error": governance_error(
                    error_type="authority-insufficient",
                    severity="error",
                    decision_id=f"authority-show:{paths.substrate_id}",
                    substrate_id=paths.substrate_id,
                    code="AUTHORITY_NOT_FOUND",
                    message=f"Authority record {paths.authority_record.name} is missing.",
                    details={"path": str(paths.authority_record)},
                ),
            }
        payload = _read_json(paths.authority_record)
        return {
            "ok": True,
            "substrate_id": paths.substrate_id,
            "authority": payload,
            "summary": {
                "owner": payload.get("owner"),
                "stewards": payload.get("stewards", []),
                "promotion_policy": payload.get("promotion_policy"),
                "risk_level": payload.get("risk_level"),
            },
        }

    def continuity_timeline(self, substrate_id: str) -> dict[str, Any]:
        normalized_id = _sanitize_substrate_id(substrate_id)
        chain = self.chain_validation_report(normalized_id)
        if not chain.get("ok"):
            return chain

        events: list[dict[str, Any]] = []
        substrate = chain["chain"]["substrate"]
        evidence = chain["chain"].get("evidence", {})
        continuity = chain["chain"].get("continuity", {})
        import_ts = evidence.get("generatedAt") or _timestamp()
        events.append(
            {
                "kind": "created",
                "timestamp": import_ts,
                "detail": {
                    "origin_repo": substrate.get("lineage", {}).get("origin_repo"),
                    "origin_path": substrate.get("lineage", {}).get("origin_path"),
                },
            }
        )
        events.append(
            {
                "kind": "imported",
                "timestamp": import_ts,
                "detail": {
                    "merge_commit": evidence.get("target", {}).get("mergeCommit"),
                    "merge_mode": evidence.get("target", {}).get("mergeMode"),
                },
            }
        )
        events.append(
            {
                "kind": "normalized",
                "timestamp": import_ts,
                "detail": {
                    "normalized_from": substrate.get("lineage", {}).get("normalized_from"),
                    "status": substrate.get("status"),
                },
            }
        )
        for decision in self.decision_log(normalized_id)["entries"]:
            events.append(
                {
                    "kind": "decision",
                    "timestamp": decision.get("checked_at", decision.get("timestamp", _timestamp())),
                    "detail": decision,
                }
            )
        if continuity:
            events.append(
                {
                    "kind": "continuity",
                    "timestamp": continuity.get("mergeCommit", import_ts),
                    "detail": continuity,
                }
            )
        events.sort(key=lambda item: (str(item.get("timestamp", "")), str(item.get("kind", ""))))
        return {"ok": True, "substrate_id": normalized_id, "timeline": events}

    def decision_log(self, substrate_id: str) -> dict[str, Any]:
        paths = self.substrate_paths(substrate_id)
        log_path = paths.logs_dir / "governance" / f"{paths.substrate_id}.log.jsonl"
        entries = _read_jsonl(log_path)
        if not entries:
            promotion_path = paths.provenance_dir / f"{paths.substrate_id}.promotion.json"
            if promotion_path.exists():
                entries.append(_read_json(promotion_path))
        return {"ok": True, "substrate_id": paths.substrate_id, "entries": entries}

    def lineage_graph(self, substrate_id: str) -> dict[str, Any]:
        timeline = self.continuity_timeline(substrate_id)
        if not timeline.get("ok"):
            return timeline
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        previous_node_id: str | None = None
        for index, event in enumerate(timeline["timeline"]):
            node_id = f"n-{index:02d}-{event['kind']}"
            node_type = {
                "created": "origin",
                "imported": "import",
                "normalized": "normalize",
                "decision": "promotion",
                "continuity": "promotion",
            }.get(str(event["kind"]), "fork")
            detail = event.get("detail", {})
            node = {
                "id": node_id,
                "type": node_type,
                "timestamp": event.get("timestamp"),
                "label": event["kind"],
                "detail": detail,
            }
            if event["kind"] == "decision":
                node["status"] = detail.get("to") or detail.get("result")
            nodes.append(node)
            if previous_node_id is not None:
                edges.append(
                    {
                        "from": previous_node_id,
                        "to": node_id,
                        "type": "evolves_to",
                    }
                )
            previous_node_id = node_id
        return {"ok": True, "substrate_id": self.substrate_paths(substrate_id).substrate_id, "nodes": nodes, "edges": edges}

    def replay(self, substrate_id: str, from_stage: str = "origin", to_stage: str = "current", mode: str = "dry-run") -> dict[str, Any]:
        timeline = self.continuity_timeline(substrate_id)
        if not timeline.get("ok"):
            return timeline
        substrate = self.load_substrate_record(substrate_id)
        seed = {
            "substrate_id": substrate.get("id"),
            "from": from_stage,
            "to": to_stage,
            "mode": mode,
            "status": substrate.get("status"),
            "import_commit": substrate.get("lineage", {}).get("import_commit"),
            "normalized_from": substrate.get("lineage", {}).get("normalized_from"),
        }
        replay_id = "rpl-" + hashlib.sha256(_stable_json(seed).encode("utf-8")).hexdigest()[:12]
        steps: list[dict[str, Any]] = []
        for index, event in enumerate(timeline["timeline"]):
            steps.append(
                {
                    "step": event["kind"],
                    "index": index,
                    "timestamp": event.get("timestamp"),
                    "status": "ok",
                    "detail": event.get("detail", {}),
                }
            )
        payload = {
            "ok": True,
            "substrate_id": substrate.get("id"),
            "replay_id": replay_id,
            "from": from_stage,
            "to": to_stage,
            "mode": mode,
            "generated_at": _timestamp(),
            "steps": steps,
        }
        log_path = self.repo_root / "logs" / "replay" / f"{self.substrate_paths(substrate_id).substrate_id}.log.jsonl"
        _append_jsonl(
            log_path,
            {
                "type": "replay",
                "replay_id": replay_id,
                "substrate_id": payload["substrate_id"],
                "from": from_stage,
                "to": to_stage,
                "mode": mode,
                "generated_at": payload["generated_at"],
                "steps": steps,
            },
        )
        return payload

    def promote(self, substrate_id: str, to_status: str, conformance_path: Path | None = None, apply: bool = True, source: str = "cli") -> dict[str, Any]:
        substrate_id = _sanitize_substrate_id(substrate_id)
        substrate = self.load_substrate_record(substrate_id)
        from_status = str(substrate.get("status", "")).strip()
        if conformance_path is None:
            default_conformance = self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.conformance.json"
            if default_conformance.exists():
                conformance_path = default_conformance
        promotion_steps = self._promotion_steps(from_status, to_status)
        if not promotion_steps and from_status != to_status:
            error = governance_error(
                error_type="promotion-contract-violation",
                severity="error",
                decision_id=self._decision_id(substrate_id, from_status, to_status, "path"),
                substrate_id=substrate_id,
                code="PROMOTION_CONTRACT_UNMET",
                message=f"no lawful promotion path from {from_status!r} to {to_status!r}",
                details={"from": from_status, "to": to_status},
            )
            return {
                "substrate_id": substrate_id,
                "from_status": from_status,
                "to_status": to_status,
                "contract_id": "ciems-standard",
                "allowed": False,
                "missing_requirements": ["lawful promotion path"],
                "substrate_path": str(self.substrate_paths(substrate_id).substrate_record),
                "decision_path": str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.promotion.json"),
                "conformance_path": str(conformance_path) if conformance_path else str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.conformance.json"),
                "checked_at": error["timestamp"],
                "status": "blocked",
                "error": error,
                "applied": False,
            }

        report: dict[str, Any] | None = None
        if from_status == to_status:
            report = {
                "substrate_id": substrate_id,
                "from_status": from_status,
                "to_status": to_status,
                "contract_id": "ciems-standard",
                "allowed": True,
                "missing_requirements": [],
                "substrate_path": str(self.substrate_paths(substrate_id).substrate_record),
                "decision_path": str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.promotion.json"),
                "conformance_path": str(conformance_path) if conformance_path else str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.conformance.json"),
                "checked_at": _timestamp(),
                "status": "promoted",
                "applied": False,
            }
        else:
            for step_status in promotion_steps:
                report = promoter.promote_substrate(
                    self.repo_root,
                    substrate_id,
                    step_status,
                    conformance_path=conformance_path,
                    apply=apply,
                )
                if not report.get("allowed"):
                    break
            if report is None:
                report = {
                    "substrate_id": substrate_id,
                    "from_status": from_status,
                    "to_status": to_status,
                    "contract_id": "ciems-standard",
                    "allowed": False,
                    "missing_requirements": ["promotion path evaluation failed"],
                    "substrate_path": str(self.substrate_paths(substrate_id).substrate_record),
                    "decision_path": str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.promotion.json"),
                    "conformance_path": str(conformance_path) if conformance_path else str(self.repo_root / "constitutional" / "provenance" / f"{substrate_id}.conformance.json"),
                    "checked_at": _timestamp(),
                    "status": "blocked",
                    "applied": False,
                }
        decision_record = {
            "type": "decision",
            "decision_id": self._decision_id(substrate_id, report["from_status"], report["to_status"], report["checked_at"]),
            "substrate_id": substrate_id,
            "source": source,
            "from": report["from_status"],
            "to": report["to_status"],
            "result": report["status"],
            "allowed": report["allowed"],
            "missing_requirements": report["missing_requirements"],
            "checked_at": report["checked_at"],
            "applied": report.get("applied", False),
            "decision_path": report.get("decision_path"),
            "substrate_path": report.get("substrate_path"),
        }
        _append_jsonl(self.repo_root / "logs" / "governance" / f"{substrate_id}.log.jsonl", decision_record)
        return report

    def submit_decision(self, substrate_id: str, decision: dict[str, Any], conformance_path: Path | None = None, source: str = "daemon") -> dict[str, Any]:
        substrate_id = _sanitize_substrate_id(substrate_id)
        action = str(decision.get("action", "")).strip().lower()
        target = str(decision.get("target") or decision.get("to") or "").strip().lower()
        requires = [str(item).strip() for item in decision.get("requires", []) if str(item).strip()]
        effects = [str(item).strip() for item in decision.get("effects", []) if str(item).strip()]
        decision_id = str(decision.get("decision_id") or decision.get("id") or self._decision_id(substrate_id, action, target, _timestamp()))
        if action != "promote":
            error = governance_error(
                error_type="runtime-invariant-violation",
                severity="error",
                decision_id=decision_id,
                substrate_id=substrate_id,
                code="RUNTIME_INVARIANT_BREACH",
                message=f"Unsupported decision action: {action!r}",
                details={"decision": decision, "requires": requires, "effects": effects},
            )
            _append_jsonl(
                self.repo_root / "logs" / "governance" / f"{substrate_id}.log.jsonl",
                {
                    "type": "decision",
                    "decision_id": decision_id,
                    "substrate_id": substrate_id,
                    "source": source,
                    "action": action,
                    "target": target,
                    "result": "blocked",
                    "error": error,
                    "requires": requires,
                    "effects": effects,
                    "checked_at": error["timestamp"],
                },
            )
            return {"result": "blocked", "error": error, "decision_id": decision_id}

        report = self.promote(substrate_id, target, conformance_path=conformance_path, apply=True, source=source)
        return {"result": "approved" if report.get("allowed") else "blocked", "decision": decision, "promotion": report}

    def substrate_detail(self, substrate_id: str) -> dict[str, Any]:
        substrate = self.load_substrate_record(substrate_id)
        chain = self.chain_validation_report(substrate_id)
        lineage = self.lineage_graph(substrate_id)
        continuity = self.continuity_timeline(substrate_id)
        return {
            "ok": True,
            "substrate": substrate,
            "chain": chain,
            "lineage": lineage,
            "continuity": continuity,
        }

    def _decision_id(self, substrate_id: str, *parts: Any) -> str:
        seed = _stable_json([substrate_id, *parts])
        return "dec-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]

    def _promotion_steps(self, from_status: str, to_status: str) -> list[str]:
        if from_status == to_status:
            return []
        if to_status == "deprecated":
            return ["deprecated"] if from_status == "active" else []
        if from_status not in PROMOTION_ORDER or to_status not in PROMOTION_ORDER:
            return []
        start_index = PROMOTION_ORDER.index(from_status)
        target_index = PROMOTION_ORDER.index(to_status)
        if target_index < start_index:
            return []
        return list(PROMOTION_ORDER[start_index + 1 : target_index + 1])

    def continuity_record(self, substrate_id: str) -> dict[str, Any]:
        paths = self.substrate_paths(substrate_id)
        if not paths.continuity_record.exists():
            return {
                "ok": False,
                "error": governance_error(
                    error_type="continuity-broken",
                    severity="error",
                    decision_id=f"continuity:{paths.substrate_id}",
                    substrate_id=paths.substrate_id,
                    code="CONTINUITY_BREAK_UNRESOLVED",
                    message=f"Continuity record {paths.continuity_record.name} is missing.",
                    details={"path": str(paths.continuity_record)},
                ),
            }
        return {"ok": True, "substrate_id": paths.substrate_id, "continuity": _read_json(paths.continuity_record)}


def ensure_text_or_json_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"value": value}
