"""Draft semantic-input adapters for non-Mythar source languages."""

from __future__ import annotations


# Specified v0.4 semantic mappings; this is not a morphological analysis of
# Mandarin or a claim that either language descends from the other.
MANDARIN_TO_MYTHAR = {
    "光": "la", "说": "ra", "神": "ia", "门": "tor", "力量": "ka",
    "风": "fu", "存在": "ma", "集体": "rum",
}

ENGLISH_TO_MYTHAR = {
    "proclamation": "ema", "declare": "ema", "existence": "ma", "ground": "ma",
    "light": "la", "illuminate": "la", "power": "ka", "test": "ka",
    "threshold": "tor", "cross": "tor", "divinity": "ia", "sanctify": "ia",
    "blessing": "fu", "carry": "fu", "speech": "ra", "speak": "ra",
    "collective": "rum", "unite": "rum",
}


def normalize_source(source: str, source_language: str) -> str:
    """Map one supported semantic-input token to Mythar source."""
    if source_language == "mythar":
        return source
    if source_language == "zh":
        return MANDARIN_TO_MYTHAR.get(source.strip(), source)
    if source_language == "en":
        return ENGLISH_TO_MYTHAR.get(source.strip().lower(), source)
    raise ValueError(f"Unsupported source_language: {source_language}")
