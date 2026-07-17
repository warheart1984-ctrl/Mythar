"""Draft semantic-input adapters for non-Mythar source languages."""

from __future__ import annotations


# Specified v0.4 semantic mappings; this is not a morphological analysis of
# Mandarin or a claim that either language descends from the other.
MANDARIN_TO_MYTHAR = {
    "光": "la", "说": "ra", "神": "ia", "门": "tor", "力量": "ka",
    "风": "fu", "存在": "ma", "集体": "rum",
}


def normalize_source(source: str, source_language: str) -> str:
    """Map one supported semantic-input token to Mythar source."""
    if source_language == "mythar":
        return source
    if source_language == "zh":
        return MANDARIN_TO_MYTHAR.get(source.strip(), source)
    raise ValueError(f"Unsupported source_language: {source_language}")
