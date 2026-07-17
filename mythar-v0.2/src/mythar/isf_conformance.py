"""Executable conformance runner for the ratified ISF v0.4 contract."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .core import MytharCompiler, REGISTRY_DIR
from .isf import to_isf
from .semantic_input import normalize_source


DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "tests" / "isf" / "v0.4"
ROOT = Path(os.getenv("MYTHAR_ISF_CONFORMANCE_ROOT", str(DEFAULT_ROOT)))


def run() -> dict[str, Any]:
    compiler = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]
    results = []
    for case in cases:
        language = case.get("source_language", "mythar")
        compilation = compiler.compile(normalize_source(case["source"], language), case.get("mode", "strict"))
        expected = case["expected"]
        passed = compilation["valid"] == expected["valid"]
        actual: dict[str, Any] = {"valid": compilation["valid"]}
        if compilation["valid"]:
            isf = to_isf(compilation, language)
            actual["isf"] = isf
            for key, value in expected.get("isf", {}).items():
                passed = passed and isf.get(key) == value
        else:
            codes = [item["error_code"] for item in compilation["diagnostics"]]
            actual["error_codes"] = codes
            passed = passed and expected.get("error_code") in codes
        results.append({"id": case["id"], "passed": passed, "actual": actual})
    return {"suite": "Mythar ISF v0.4", "total": len(results), "passed": sum(item["passed"] for item in results), "failed": sum(not item["passed"] for item in results), "results": results}
