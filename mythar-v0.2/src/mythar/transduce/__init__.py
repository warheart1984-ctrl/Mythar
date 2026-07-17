"""Language transducers that consume Mythar ISF."""

from .english import mythar_to_english, translate_isf
from .mandarin import translate_isf as translate_isf_to_mandarin

__all__ = ["mythar_to_english", "translate_isf", "translate_isf_to_mandarin"]
