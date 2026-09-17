"""de / da / ki / mi motoru (Bölüm 9).

Standalone "de", "da", "ki" ve soru eki ("mi/mı/mu/mü" + varyantları,
ör. "musun") token'larını, zeyrek'in morfolojik analiziyle bağlaç/soru
eki olarak doğrulayıp önceki kelimeyle bitiştirir:

    ben de geleceğim  -> bende geleceğim   (sonra predicate_rules ile) -> bende gelicem
    öyle ki           -> öyleki
    geliyor musun     -> geliyormusun

Kör string.replace() KULLANILMAZ: "evde" gibi kelimelerde "de" zaten
bulunma hali ekidir ve ayrı bir token olarak hiç görünmez (tokenizer
"evde"yi tek parça olarak ayırır), bu yüzden yanlışlıkla dokunulmaz.
Ayrıca zeyrek'in aday parse listesinde ilgili POS (Conj/Ques) yoksa
(örn. "de" burada "demek" fiilinin emir kipiyse) dönüşüm uygulanmaz.

Sınırlama: zeyrek bir istatistiksel disambiguator içermediği için
"bu POS olası mı" sorusuna cevap verebiliyoruz, "bağlamda kesin doğru
okuma bu mu" sorusuna veremiyoruz (bkz. app/morphology/analyzer.py
docstring'i). Bu yüzden dönüşüm olasılıksaldır (persona rate ile
kontrol edilir), kör/deterministik değildir.
"""
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from app.error_engine import scoring
from app.guardian.protected_tokens import find_protected_spans, is_inside_protected
from app.morphology import analyzer
from app.morphology.tokenizer import tokenize

_DE_DA_WORDS = {"de", "da"}
_KI_WORDS = {"ki"}


@dataclass
class JoinChange:
    rule: str
    before: str
    after: str
    probability: float


def _is_conjunction(word: str) -> bool:
    return "Conj" in analyzer.pos_tags(word)


def _is_question_particle(word: str) -> bool:
    lower = word.lower()
    if not lower.startswith(("mi", "mı", "mu", "mü")):
        return False
    return "Ques" in analyzer.pos_tags(word)


def apply(text: str, base_weights: Dict[str, float], rate: float, rng: random.Random) -> Tuple[str, List[JoinChange]]:
    protected_spans = find_protected_spans(text)
    tokens = tokenize(text)

    changes: List[JoinChange] = []
    join_before: List[int] = []

    for i in range(1, len(tokens)):
        prev, cur = tokens[i - 1], tokens[i]
        if not prev.is_word or not cur.is_word:
            continue
        if text[prev.end:cur.start] != " ":
            continue
        if is_inside_protected(prev.start, protected_spans) or is_inside_protected(cur.start, protected_spans):
            continue

        lower = cur.text.lower()
        rule = None
        weight_key = None
        if lower in _DE_DA_WORDS and _is_conjunction(cur.text):
            rule, weight_key = "de_da_join", "de_da"
        elif lower in _KI_WORDS and _is_conjunction(cur.text):
            rule, weight_key = "ki_join", "ki"
        elif _is_question_particle(cur.text):
            rule, weight_key = "mi_join", "mi"

        if rule is None:
            continue

        prob = scoring.error_score(base_weights.get(weight_key, 1.0), rate)
        if rng.random() >= prob:
            continue

        join_before.append(i)
        changes.append(JoinChange(
            rule=rule, before=f"{prev.text} {cur.text}", after=f"{prev.text}{cur.text}", probability=prob,
        ))

    if not join_before:
        return text, []

    join_set = set(join_before)
    parts: List[str] = []
    last_end = 0
    for i, token in enumerate(tokens):
        gap_end = token.start - 1 if i in join_set else token.start
        parts.append(text[last_end:gap_end])
        parts.append(token.text)
        last_end = token.end
    parts.append(text[last_end:])
    return "".join(parts), changes
