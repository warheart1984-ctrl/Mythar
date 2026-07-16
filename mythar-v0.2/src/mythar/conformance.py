from __future__ import annotations

import json
from pathlib import Path

from .core import MytharCompiler

ROOT = Path(r"G:\mythar-registry\tests\v0.2")

def run() -> dict:
    compiler = MytharCompiler(); cases = []
    for path in ROOT.glob("*/*.json"):
        cases.extend(json.loads(path.read_text(encoding="utf-8"))["cases"])
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
        passed = result["valid"] == case["valid"] and all(code in codes for code in case.get("errors", []))
        results.append({"id":case["id"],"passed":passed,"actual_errors":codes})
    return {"total":len(results),"passed":sum(item["passed"] for item in results),"failed":sum(not item["passed"] for item in results),"results":results}
