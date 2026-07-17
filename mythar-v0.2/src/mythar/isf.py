"""Intermediate Semantic Form (ISF) v0.4 generation."""

from __future__ import annotations

from typing import Any


# Specified semantic profiles for ISF v0.4. These are language-engineering
# design data, not claims of historical reconstruction.
ROOT_PROFILES = {
    "ema": {"class": "proclamation", "domain": "speech", "intent": "declare"},
    "ma": {"class": "existence", "domain": "being", "intent": "ground"},
    "la": {"class": "illumination", "domain": "truth", "intent": "reveal"},
    "ka": {"class": "power", "domain": "time", "intent": "test"},
    "tor": {"class": "threshold", "domain": "boundary", "intent": "cross"},
    "ia": {"class": "divinity", "domain": "sacred", "intent": "sanctify"},
    "fu": {"class": "blessing", "domain": "wind", "intent": "carry"},
    "ra": {"class": "proclamation", "domain": "speech", "intent": "speak"},
    "rum": {"class": "collective", "domain": "assembly", "intent": "unite"},
}


def to_isf(compilation: dict[str, Any], source_language: str = "mythar") -> dict[str, Any]:
    """Convert one valid Mythar compilation result to an ISF v0.4 node."""
    if not compilation["valid"]:
        raise ValueError("ISF can only be generated from a valid Mythar compilation.")

    clause = compilation["ast"]["clauses"][0]
    terms = clause["terms"]
    if len(terms) != 1:
        raise ValueError("ISF v0.4 requires exactly one semantic root per expression.")

    node = terms[0]
    operators: list[str] = []
    while node.get("kind") == "OperatorApplication":
        operators.append(node["operator_form"])
        node = node["target"]

    root = _root_for(node)
    profile = ROOT_PROFILES.get(root)
    canonical = node.get("kind") in {"Root", "Composite"}
    notes: list[str] = []
    if profile is None:
        profile = {"class": "unclassified", "domain": "unspecified", "intent": "unspecified"}
        notes.append(f"No specified ISF v0.4 profile exists for root '{root}'.")

    return {
        "version": "0.4",
        "root": root,
        "canonical": canonical,
        **profile,
        "operators": list(reversed(operators)),
        "arguments": [],
        "context": {
            "source_language": source_language,
            "compiler_version": "v2",
            "line": 1,
            "column": (node.get("token_index") or 0) + 1,
        },
        "metadata": {"confidence": 1.0 if canonical and not notes else 0.5, "notes": notes},
    }


def _root_for(node: dict[str, Any]) -> str:
    if node.get("kind") == "Root":
        return node["surface"]
    if node.get("kind") == "Composite":
        components = node.get("components", [])
        if components:
            return components[0].removeprefix("ROOT-").lower()
    raise ValueError("ISF v0.4 requires a root or composite semantic target.")
