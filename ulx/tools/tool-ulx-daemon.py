#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ulx_governance.daemon import serve  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ulx-daemon", description="Run the ULX daemon.")
    parser.add_argument("--repo-root", default="", help="ULX repository root (defaults to discovery).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8799)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    serve(repo_root=repo_root, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

