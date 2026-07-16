from __future__ import annotations

import json
import os
from pathlib import Path

from .core import BASE, EXTENSION, REGISTRY_DIR, MytharCompiler

ROOT = Path(os.getenv("MYTHAR_CONFORMANCE_ROOT", REGISTRY_DIR / "tests" / "v0.2"))

def run() -> dict:
    extension = REGISTRY_DIR / "registry-v0.3.json" if ROOT.name == "v0.3" else EXTENSION
    compiler = MytharCompiler(BASE, extension)
    cases = []
    paths = [*ROOT.glob("*.json"), *ROOT.glob("*/*.json")]
    for path in paths:
        cases.extend(json.loads(path.read_text(encoding="utf-8"))["cases"])
    if ROOT.name != "v0.3":
        safe_prefix_targets = [form for form in compiler.roots if form not in compiler.suffixes]
        for form in compiler.roots:
            cases.append({"id": f"matrix-root-{form}", "input": form, "valid": True})
            cases.append({"id": f"matrix-frame-ja-{form}", "input": f"ja {form}", "valid": True})
            cases.append({"id": f"matrix-case-{form}", "input": f"ja fa {form} ko", "valid": True})
        for prefix in compiler.prefixes:
            for form in safe_prefix_targets:
                cases.append({"id": f"matrix-prefix-{prefix}-{form}", "input": f"ja {prefix}-{form}", "valid": True})
        for suffix in compiler.suffixes:
            cases.append({"id": f"matrix-suffix-fa-{suffix}", "input": f"ja fa-{suffix}", "valid": True})
        for particle in compiler.particles:
            cases.append({"id": f"matrix-stack-{particle}", "input": f"{particle} la tor", "valid": True})
    results = []
    for case in cases:
        result = compiler.compile(case["input"], case.get("mode", "strict"))
        codes = [item["error_code"] for item in result["diagnostics"]]
        passed = _matches_case(case, result, codes)
        results.append({"id":case["id"],"passed":passed,"actual_errors":codes})
    return {"total":len(results),"passed":sum(item["passed"] for item in results),"failed":sum(not item["passed"] for item in results),"results":results}


def _matches_case(case: dict, result: dict, codes: list[str]) -> bool:
    """Support both frozen v0.2 cases and the v0.3 ratification schema."""
    if "valid" in case:
        return result["valid"] == case["valid"] and all(code in codes for code in case.get("errors", []))

    clause = result["ast"]["clauses"][0]
    terms = clause["terms"]
    expected_error = case.get("expected_error_code")
    if expected_error:
        return not result["valid"] and expected_error in codes

    expected_ast = case.get("expected_ast")
    if expected_ast:
        if not result["valid"] or len(terms) != 1:
            return False
        node = terms[0]
        if node.get("kind") != expected_ast.get("kind"):
            return False
        if "registry_ref" in expected_ast and node.get("registry_ref") != expected_ast["registry_ref"]:
            return False
        if "operator_ref" in expected_ast and node.get("operator_ref") != expected_ast["operator_ref"]:
            return False
        if "target_ref" in expected_ast and node.get("target", {}).get("registry_ref") != expected_ast["target_ref"]:
            return False
        return True

    expected_stack = case.get("expected_particle_stack")
    if expected_stack is not None:
        actual_stack = [item.get("registry_ref") for item in clause["particle_stack"]]
        return result["valid"] and actual_stack == expected_stack

    return False
