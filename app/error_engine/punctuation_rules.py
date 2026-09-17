"""Noktalama / biçimlendirme hataları (Bölüm 13)."""
import random
import re


def drop_oxford_comma_before_baglac(text: str, rng: random.Random, rate: float) -> str:
    """', ve' / ', ama' gibi bağlaç öncesi virgülleri düşük olasılıkla kaldırır."""
    def maybe_drop(match: "re.Match") -> str:
        return match.group(1) if rng.random() < rate else match.group(0)

    return re.sub(r",( (ve|ama|fakat|ancak) )", maybe_drop, text)


def drop_trailing_period(text: str, rng: random.Random, rate: float) -> str:
    if text.endswith(".") and rng.random() < rate:
        return text[:-1]
    return text


def lowercase_sentence_start(text: str, rng: random.Random, rate: float) -> str:
    if text and text[0].isupper() and rng.random() < rate:
        return text[0].lower() + text[1:]
    return text


def add_extra_space(text: str, rng: random.Random, rate: float) -> str:
    if rng.random() >= rate:
        return text
    spaces = [m.start() for m in re.finditer(r" ", text)]
    if not spaces:
        return text
    idx = rng.choice(spaces)
    return text[:idx] + "  " + text[idx + 1:]
