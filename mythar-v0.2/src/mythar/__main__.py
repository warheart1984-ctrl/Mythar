import argparse, json, sys
from .api import serve
from .conformance import run
from .core import MytharCompiler, REGISTRY_DIR
from .isf import to_isf
from .semantic_input import normalize_source
from .transduce.english import translate_isf
from .transduce.mandarin import translate_isf as translate_to_mandarin

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

parser = argparse.ArgumentParser(prog="mythar")
commands = parser.add_subparsers(dest="command", required=True)
compile_cmd = commands.add_parser("compile"); compile_cmd.add_argument("expression"); compile_cmd.add_argument("--mode", choices=["strict","lenient"], default="strict")
translate_cmd = commands.add_parser("translate"); translate_cmd.add_argument("source"); translate_cmd.add_argument("--source-language", choices=["mythar", "en", "zh"], default="mythar"); translate_cmd.add_argument("--target-language", choices=["en", "zh"], default="en")
serve_cmd = commands.add_parser("serve"); serve_cmd.add_argument("--port", type=int, default=8080); serve_cmd.add_argument("--host", default="127.0.0.1")
commands.add_parser("test")
args = parser.parse_args()
if args.command == "compile":
    output = MytharCompiler().compile(args.expression, args.mode); print(json.dumps(output, indent=2, ensure_ascii=False)); sys.exit(0 if output["valid"] else 2)
if args.command == "translate":
    compiler = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")
    result = compiler.compile(normalize_source(args.source, args.source_language))
    if not result["valid"]:
        print(json.dumps(result, indent=2, ensure_ascii=False)); sys.exit(2)
    isf = to_isf(result, args.source_language)
    print(translate_isf(isf) if args.target_language == "en" else translate_to_mandarin(isf))
    sys.exit(0)
if args.command == "serve": serve(args.port, args.host)
report = run(); print(json.dumps(report, indent=2, ensure_ascii=False)); sys.exit(0 if report["failed"] == 0 else 1)
