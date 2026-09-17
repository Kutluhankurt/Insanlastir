"""Sözlük tabanlı sözcük/deyim hataları (Bölüm 7-8).

human_error_dictionary.json (çok varyantlı, olasılıklı) ve
known_mistakes.json (tek varyantlı, sabit) dosyalarını yükler ve
metindeki geçişleri bulur.
"""
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@dataclass
class LexicalVariant:
    value: str
    weight: float
    error_type: str
    styles: List[str]
    semantic_risk: str


@dataclass
class LexicalEntry:
    correct: str
    variants: List[LexicalVariant]


def load_dictionary(path: Optional[Path] = None) -> List[LexicalEntry]:
    path = path or (_DATA_DIR / "human_error_dictionary.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    entries = []
    for item in raw["entries"]:
        variants = [
            LexicalVariant(
                value=v["value"],
                weight=v["weight"],
                error_type=v["error_type"],
                styles=v["styles"],
                semantic_risk=v["semantic_risk"],
            )
            for v in item["variants"]
        ]
        entries.append(LexicalEntry(correct=item["correct"], variants=variants))
    return entries


def load_known_mistakes(path: Optional[Path] = None) -> Dict[str, str]:
    path = path or (_DATA_DIR / "known_mistakes.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return dict(raw["entries"])


def pick_variant(entry: LexicalEntry, style: str, rng: random.Random) -> Optional[LexicalVariant]:
    """Verilen stile uygun varyantlar arasından ağırlıklı seçim yapar."""
    candidates = [v for v in entry.variants if style in v.styles or not v.styles]
    if not candidates:
        return None
    weights = [v.weight for v in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def apply_dictionary(text: str, entries: List[LexicalEntry], style: str, rate: float, rng: random.Random) -> str:
    """Sözlükteki `correct` ifadelerini metinde arar, olasılıkla değiştirir.

    Not: Faz 1'de basit substring eşleşmesi kullanılır; korunan token'ların
    (Bölüm 16) içine denk gelmemesi guardian.protected_tokens tarafından
    çağıran katmanda garanti edilmelidir.
    """
    result = text
    for entry in entries:
        if entry.correct not in result:
            continue
        if rng.random() > rate:
            continue
        variant = pick_variant(entry, style, rng)
        if variant is None:
            continue
        result = result.replace(entry.correct, variant.value, 1)
    return result


def apply_known_mistakes(text: str, mistakes: Dict[str, str], rate: float, rng: random.Random) -> str:
    result = text
    for correct, wrong in mistakes.items():
        if correct not in result:
            continue
        if rng.random() > rate:
            continue
        result = result.replace(correct, wrong, 1)
    return result
