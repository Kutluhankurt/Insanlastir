"""Typo Engine (Bölüm 12).

Typo oranı kasıtlı olarak düşük tutulmalıdır; asıl değer predicate/lexical
katmanlarındadır (bkz. plan Bölüm 44 madde 5).
"""
import random
from typing import Optional

# Türkçe Q klavye komşuluk haritası (basitleştirilmiş).
_ADJACENT = {
    "a": "sq", "s": "ade", "d": "sfe", "f": "dg", "g": "fh",
    "e": "wr3sd", "r": "edt4", "t": "ry5", "y": "tu6", "u": "yı7",
    "ı": "u8i", "i": "ıo9", "o": "ip0", "p": "oğ",
    "k": "jl", "l": "kş", "m": "n", "n": "bm",
}

_TURKISH_TO_ASCII = str.maketrans("şğıöüç", "sgiouc")


def delete_char(word: str, rng: random.Random) -> Optional[str]:
    if len(word) < 3:
        return None
    idx = rng.randrange(1, len(word) - 1)
    return word[:idx] + word[idx + 1:]


def duplicate_char(word: str, rng: random.Random) -> Optional[str]:
    if len(word) < 2:
        return None
    idx = rng.randrange(len(word))
    return word[: idx + 1] + word[idx] + word[idx + 1:]


def adjacent_key_typo(word: str, rng: random.Random) -> Optional[str]:
    if len(word) < 3:
        return None
    idx = rng.randrange(len(word))
    ch = word[idx].lower()
    options = _ADJACENT.get(ch)
    if not options:
        return None
    replacement = rng.choice(options)
    return word[:idx] + replacement + word[idx + 1:]


def turkish_char_normalize(word: str) -> str:
    """ş->s, ğ->g, ı->i, ö->o, ü->u, ç->c."""
    return word.translate(_TURKISH_TO_ASCII)


_TYPO_FNS = (delete_char, duplicate_char, adjacent_key_typo)


def apply_random_typo(word: str, rng: random.Random) -> Optional[str]:
    fn = rng.choice(_TYPO_FNS)
    return fn(word, rng)
