"""English transduction for ISF v0.4, using only the Python standard library."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..isf import to_isf


def _contract_path() -> Path:
    """Find the source-checkout contract or an explicitly configured contract."""
    configured = os.getenv("MYTHAR_TRANSDUCER_DIR")
    candidates = [Path(configured).expanduser()] if configured else []
    candidates.append(Path(__file__).resolve().parents[3] / "transducers")
    for directory in candidates:
        path = directory / "en.json"
        if path.is_file():
            return path
    raise FileNotFoundError(
        "English transduction contract not found. Set MYTHAR_TRANSDUCER_DIR "
        "to a directory containing en.json."
    )


def _mappings() -> dict[str, dict[str, str]]:
    return json.loads(_contract_path().read_text(encoding="utf-8"))["mappings"]


def translate_isf(isf: dict[str, Any]) -> str:
    """Convert one ISF v0.4 node into a deterministic English phrase."""
    root = isf.get("root")
    mapping = _mappings().get(root)
    if mapping is None:
        return f"[unmapped:{root}]"

    semantic_class = isf.get("class")
    word = mapping["verb"] if semantic_class in {"proclamation", "illumination"} else mapping["noun"]
    arguments = [translate_isf(argument) for argument in isf.get("arguments", [])]
    return " ".join([word, *arguments])


def mythar_to_english(source: str, compiler: Any) -> str:
    """Compile source with a v2-compatible compiler and transduce its ISF."""
    compilation = compiler.compile(source)
    return translate_isf(to_isf(compilation))
