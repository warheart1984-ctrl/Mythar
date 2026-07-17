"""Repository-local AAES-OS integration envelope for Mythar artifacts."""

from __future__ import annotations

from typing import Any

from .isf import to_isf


def to_aaes_envelope(compilation: dict[str, Any], source_language: str = "mythar") -> dict[str, Any]:
    """Project a valid Mythar compilation into typed AAES-OS integration surfaces."""
    if not compilation["valid"]:
        raise ValueError("AAES integration requires a valid Mythar compilation.")
    isf = to_isf(compilation, source_language)
    invariants = compilation["invariants"]
    return {
        "version": "0.1",
        "domain": "Mythar Constitutional Semantic Domain",
        "cmm": {"semantic_primitives": {"ast": compilation["ast"], "isf": isf}},
        "cem": {"evidence": {"registry_refs": compilation["registry_refs"], "diagnostics": compilation["diagnostics"]}, "invariant_outcomes": invariants},
        "css": {"domain_specification": "Mythar DCS", "platform_independent": True},
        "ccs": {"conformance_profile": "Mythar Core v0.2 + v0.3 + ISF v0.4", "invariants_passed": all(item["passed"] for item in invariants)},
        "dos": {"typed_decision_input": {"ast": compilation["ast"], "isf": isf}, "decision_graph_status": "candidate-input"},
        "ccr": {"canonical_state": "AST + ISF + registry references", "rendering": "projection-only"},
        "promotion_sequence": {"state": "substrate", "lineage_refs": compilation["registry_refs"], "stewardship": "versioned registry, conformance, ratification, release"},
        "integration_boundaries": {
            "ciems": "declared-governance-integration-pending-executable-contract",
            "civca_x": "declared-domain-integration-pending-executable-contract",
            "voss": "declared-domain-integration-pending-executable-contract",
        },
    }
