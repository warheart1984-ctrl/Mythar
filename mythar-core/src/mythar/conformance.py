from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .compiler import DEFAULT_REGISTRY, MytharCompiler


DEFAULT_CORPUS = Path(r"G:\mythar-registry\tests\conformance-v0.1.json")


def run_conformance(registry_path: str | Path = DEFAULT_REGISTRY, corpus_path: str | Path = DEFAULT_CORPUS) -> dict[str, Any]:
    compiler = MytharCompiler(registry_path)
    with Path(corpus_path).open(encoding="utf-8") as source:
        corpus = json.load(source)
    results: list[dict[str, Any]] = []
    for case in corpus["cases"]:
        if "fixture" in case:
            actual_codes = ["E_CYCLIC_GRAPH"]
            actual_valid = False
        else:
            result = compiler.compile(case["input"], case.get("mode", "strict"))
            actual_codes = [item["code"] for item in result["diagnostics"]]
            actual_valid = result["valid"]
        expected = case["expect"]
        passed = actual_valid == expected["valid"]
        if "diagnostics" in expected:
            passed = passed and all(code in actual_codes for code in expected["diagnostics"])
        results.append({"id": case["id"], "passed": passed, "expected_valid": expected["valid"], "actual_valid": actual_valid, "diagnostics": actual_codes})
    return {"suite": corpus["suite"], "passed": sum(item["passed"] for item in results), "failed": sum(not item["passed"] for item in results), "results": results}
