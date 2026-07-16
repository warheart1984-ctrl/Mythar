from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compiler import DEFAULT_REGISTRY, MytharCompiler
from .conformance import run_conformance


def main() -> int:
    parser = argparse.ArgumentParser(prog="mythar", description="Mythar Constitutional Registry reference compiler")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Path to a Constitutional Registry JSON file")
    commands = parser.add_subparsers(dest="command", required=True)
    compile_parser = commands.add_parser("compile", help="Compile a Mythar expression")
    compile_parser.add_argument("expression")
    compile_parser.add_argument("--mode", choices=["strict", "exploratory"], default="strict")
    commands.add_parser("test", help="Run the Constitutional Registry conformance corpus")
    args = parser.parse_args()

    if args.command == "compile":
        result = MytharCompiler(args.registry).compile(args.expression, args.mode)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["valid"] else 2
    report = run_conformance(args.registry)
    print(json.dumps(report, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
