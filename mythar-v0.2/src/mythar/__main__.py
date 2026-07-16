import argparse, json, sys
from .api import serve
from .conformance import run
from .core import MytharCompiler

parser = argparse.ArgumentParser(prog="mythar")
commands = parser.add_subparsers(dest="command", required=True)
compile_cmd = commands.add_parser("compile"); compile_cmd.add_argument("expression"); compile_cmd.add_argument("--mode", choices=["strict","lenient"], default="strict")
serve_cmd = commands.add_parser("serve"); serve_cmd.add_argument("--port", type=int, default=8080); serve_cmd.add_argument("--host", default="127.0.0.1")
commands.add_parser("test")
args = parser.parse_args()
if args.command == "compile":
    output = MytharCompiler().compile(args.expression, args.mode); print(json.dumps(output, indent=2)); sys.exit(0 if output["valid"] else 2)
if args.command == "serve": serve(args.port, args.host)
report = run(); print(json.dumps(report, indent=2)); sys.exit(0 if report["failed"] == 0 else 1)
