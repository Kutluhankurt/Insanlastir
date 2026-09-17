"""Yüklem/fiil çekim dönüşümleri (Bölüm 6).

Düz string.replace() yerine Türkçe ünlü uyumunu hesaba katan bir yaklaşım
kullanılır: -acağım/-eceğim gibi ekler atılıp gövdenin son ünlüsüne göre
dar ünlü (ı/i/u/ü) seçilerek konuşma dili varyantı üretilir.

Örnek:
    yapacağım -> yap (gövde) -> son ünlü "a" -> dar "ı" -> yapıcam
    olacağım  -> ol (gövde)  -> son ünlü "o" -> dar "u" -> olucam
"""
from dataclasses import dataclass
from typing import Optional

_VOWELS = "aeıioöuü"

# 4 yönlü ünlü uyumu: gövdenin son ünlüsü -> ekte kullanılacak dar ünlü
_NARROW_VOWEL_MAP = {
    "a": "ı", "ı": "ı",
    "e": "i", "i": "i",
    "o": "u", "u": "u",
    "ö": "ü", "ü": "ü",
}

_YOR_SUFFIXES = {
    "yorum": "yom",
    "yoruz": "yoz",
}

_FUTURE_SUFFIXES_1SG = ("acağım", "eceğim")
_FUTURE_SUFFIXES_1PL = ("acağız", "eceğiz")


@dataclass
class TransformResult:
    rule: str
    before: str
    after: str


def _son_unlu(stem: str) -> Optional[str]:
    for ch in reversed(stem.lower()):
        if ch in _VOWELS:
            return ch
    return None


def _future_casual(word: str, suffixes: tuple, trailing_consonant: str, rule_name: str) -> Optional[TransformResult]:
    """Gövde + dar ünlü (4 yönlü) + 'c' + a/e (2 yönlü) + kişi ünsüzü.

    Örnek: yap(ıcam) -> narrow='ı' (arka) -> ikinci ünlü 'a' -> "ıcam"
           gel(icem) -> narrow='i' (ön)   -> ikinci ünlü 'e' -> "icem"
    """
    lower = word.lower()
    for suf in suffixes:
        if lower.endswith(suf):
            stem = word[: -len(suf)]
            vowel = _son_unlu(stem)
            if vowel is None:
                return None
            narrow = _NARROW_VOWEL_MAP[vowel]
            second_vowel = "a" if narrow in ("ı", "u") else "e"
            after = f"{stem}{narrow}c{second_vowel}{trailing_consonant}"
            return TransformResult(rule=rule_name, before=word, after=after)
    return None


def transform_yor(word: str) -> Optional[TransformResult]:
    """-yorum -> -yom, -yoruz -> -yoz."""
    lower = word.lower()
    for suf, replacement in _YOR_SUFFIXES.items():
        if lower.endswith(suf):
            after = word[: -len(suf)] + replacement
            rule = "yor_1sg_spoken" if suf == "yorum" else "yor_1pl_spoken"
            return TransformResult(rule=rule, before=word, after=after)
    return None


def transform_future_1sg(word: str) -> Optional[TransformResult]:
    """-acağım/-eceğim -> gövde + dar ünlü + c(a/e)m."""
    return _future_casual(word, _FUTURE_SUFFIXES_1SG, "m", "future_1sg_spoken")


def transform_future_1pl(word: str) -> Optional[TransformResult]:
    """-acağız/-eceğiz -> gövde + dar ünlü + c(a/e)z."""
    return _future_casual(word, _FUTURE_SUFFIXES_1PL, "z", "future_1pl_spoken")


_ALL_TRANSFORMS = (transform_yor, transform_future_1sg, transform_future_1pl)


def apply_first_matching(word: str) -> Optional[TransformResult]:
    """Kelimeye uygulanabilecek ilk yüklem dönüşümünü döner (varsa)."""
    for fn in _ALL_TRANSFORMS:
        result = fn(word)
        if result is not None:
            return result
    return None
