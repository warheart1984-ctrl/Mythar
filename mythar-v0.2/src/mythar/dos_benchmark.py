"""Draft Mythar-backed decision-trace benchmark adapter for DOS evidence."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .core import MytharCompiler, REGISTRY_DIR
from .isf import to_isf


def a01_lexeme_ratification_run() -> dict[str, Any]:
    """Produce a deterministic reference decision trace for the `ema` case."""
    compiler = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")
    compilation = compiler.compile("ema")
    if not compilation["valid"]:
        raise RuntimeError("A01 precondition failed: ema must compile validly.")
    isf = to_isf(compilation)
    evidence_refs = ["ROOT-EMA", "mythar-registry/registry-v0.3.json", "mythar-registry/RATIFICATION-v0.3.md"]
    nodes = [
        {"id": "observe", "primitive": "Observe", "input_type": "MytharAST", "evidence": ["ROOT-EMA"]},
        {"id": "interpret", "primitive": "Interpret", "input_type": "SemanticRegistryArtifact", "evidence": evidence_refs[:2]},
        {"id": "infer", "primitive": "Infer", "input_type": "IntermediateSemanticForm", "evidence": ["ROOT-EMA"]},
        {"id": "challenge", "primitive": "Challenge", "input_type": "InvariantOutcomeRecord", "evidence": ["INV-001", "INV-004"]},
        {"id": "commit", "primitive": "Commit", "input_type": "DecisionObject", "evidence": evidence_refs},
    ]
    invariants = {
        "DOS-INV-001-no-commit-without-evidence": bool(nodes[-1]["evidence"]),
        "DOS-INV-002-typed-inputs": all(node["input_type"] for node in nodes),
        "MYTHAR-invariants": all(item["passed"] for item in compilation["invariants"]),
    }
    graph = {
        "case_id": "A01", "profile_version": "v0.1", "registry_version": "v0.3.0",
        "input": "ema", "ast": compilation["ast"], "isf": isf, "diagnostics": compilation["diagnostics"],
        "nodes": nodes, "edges": [[nodes[index]["id"], nodes[index + 1]["id"]] for index in range(len(nodes) - 1)],
        "decision": {"outcome": "retain-ratified-lexeme", "evidence_refs": evidence_refs},
    }
    graph_hash = hashlib.sha256(json.dumps(graph, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"decision_graph": graph, "graph_hash": graph_hash, "invariant_outcomes": invariants, "replay_record": {"case_id": "A01", "input": "ema", "expected_graph_hash": graph_hash, "replayable": True}}


def run_a01_benchmark(runs: int = 3) -> dict[str, Any]:
    if runs < 3:
        raise ValueError("A01 benchmark requires at least three runs.")
    records = [a01_lexeme_ratification_run() for _ in range(runs)]
    hashes = [record["graph_hash"] for record in records]
    return {"case_id": "A01", "runs": runs, "hashes": hashes, "deterministic": len(set(hashes)) == 1, "traceability_complete": all(record["invariant_outcomes"].values() for record in records), "reference_record": records[0]}
