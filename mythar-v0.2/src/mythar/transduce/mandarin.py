"""Standard Mandarin transduction for ISF v0.4."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _mappings() -> dict[str, dict[str, str]]:
    configured = os.getenv("MYTHAR_TRANSDUCER_DIR")
    directories = [Path(configured).expanduser()] if configured else []
    directories.append(Path(__file__).resolve().parents[3] / "transducers")
    for directory in directories:
        path = directory / "zh.json"
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))["mappings"]
    raise FileNotFoundError("Mandarin contract not found. Set MYTHAR_TRANSDUCER_DIR to a directory containing zh.json.")


def translate_isf(isf: dict[str, Any]) -> str:
    """Convert one ISF v0.4 node into a deterministic Mandarin phrase."""
    root = isf.get("root")
    mapping = _mappings().get(root)
    if mapping is None:
        return f"[未映射:{root}]"

    semantic_class = isf.get("class")
    word = mapping["verb"] if semantic_class in {"proclamation", "illumination"} else mapping["noun"]
    arguments = [translate_isf(argument) for argument in isf.get("arguments", [])]
    return "".join([word, *arguments])
