"""Human Error Engine orchestrator (Bölüm 4, Bölüm 25 ana mimari).

Pipeline (Faz 1 kapsamı - Naturalizer şu an no-op):

    text -> naturalizer (no-op) -> protected span tespiti -> tokenize
         -> predicate + typo (token bazlı) -> lexical dictionary (metin bazlı)
         -> punctuation -> Quality Gate -> HumanizeResult
"""
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.error_engine import lexical_rules, predicate_rules, punctuation_rules, scoring, typo_rules
from app.guardian import quality_gate as quality_gate_module
from app.guardian.protected_tokens import find_protected_spans, is_inside_protected
from app.morphology.tokenizer import tokenize
from app.naturalizer.naturalizer import naturalize

_ROOT = Path(__file__).resolve().parent.parent.parent
_PERSONAS_DIR = _ROOT / "app" / "personas"
_DATA_DIR = _ROOT / "data"

RULE_ENGINE_VERSION = "0.1.0"

_PREDICATE_RULE_TO_WEIGHT_KEY = {
    "yor_1sg_spoken": "verb_yor",
    "yor_1pl_spoken": "verb_yor",
    "future_1sg_spoken": "future_acak_ecek",
    "future_1pl_spoken": "future_acak_ecek",
}


@dataclass
class ChangeTrace:
    rule: str
    before: str
    after: str
    probability: float
    triggered: bool
    dictionary_version: str
    rule_engine_version: str
    seed: Optional[int]
    fallback_level: int


@dataclass
class HumanizeResult:
    original: str
    output: str
    style: str
    changes: List[ChangeTrace] = field(default_factory=list)
    quality_gate: Optional[quality_gate_module.QualityGateResult] = None
    seed: Optional[int] = None
    fallback_level: int = 0


def load_persona(style: str) -> Dict[str, Any]:
    path = _PERSONAS_DIR / f"{style}.yaml"
    if not path.exists():
        raise ValueError(f"Bilinmeyen persona: {style}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_predicate_weights() -> Dict[str, Any]:
    with open(_DATA_DIR / "predicate_patterns.json", encoding="utf-8") as f:
        return json.load(f)


def humanize(
    text: str,
    style: str = "technical_engineer",
    seed: Optional[int] = None,
    error_level: int = 2,
) -> HumanizeResult:
    """Ana giriş noktası. Bölüm 29'daki API şemasına karşılık gelir.

    error_level (Bölüm 21): 0=Clean (yalnızca naturalizer, hata yok)
    Faz 1'de yüklem/sözlük/typo/punctuation hepsi error_level >= 1 iken
    aktiftir; error_level=0 yalnızca naturalize() sonucunu döner.
    """
    rng = random.Random(seed)
    persona = load_persona(style)
    predicate_weights = _load_predicate_weights()
    lexical_entries = lexical_rules.load_dictionary()
    known_mistakes = lexical_rules.load_known_mistakes()

    changes: List[ChangeTrace] = []
    dictionary_version = json.load(open(_DATA_DIR / "human_error_dictionary.json", encoding="utf-8"))["version"]

    naturalized = naturalize(text, style)

    if error_level == 0:
        return HumanizeResult(original=text, output=naturalized, style=style, changes=[], seed=seed)

    errors = persona.get("errors", {})
    protected_spans = find_protected_spans(naturalized)
    tokens = tokenize(naturalized)

    output_parts: List[str] = []
    last_end = 0
    error_count = 0

    for token in tokens:
        output_parts.append(naturalized[last_end:token.start])
        last_end = token.end

        word = token.text
        if not token.is_word or is_inside_protected(token.start, protected_spans):
            output_parts.append(word)
            continue

        transformed = word
        predicate_rate = errors.get("predicate_variation_rate", 0.0)
        match = predicate_rules.apply_first_matching(word)
        if match is not None:
            weight_key = _PREDICATE_RULE_TO_WEIGHT_KEY.get(match.rule, "predicate")
            base_weight = predicate_weights["base_weights"].get(weight_key, 1.0)
            prob = scoring.error_score(base_weight, predicate_rate)
            triggered = rng.random() < prob
            changes.append(ChangeTrace(
                rule=match.rule, before=word, after=match.after, probability=prob,
                triggered=triggered, dictionary_version=dictionary_version,
                rule_engine_version=RULE_ENGINE_VERSION, seed=seed, fallback_level=0,
            ))
            if triggered:
                transformed = match.after
                error_count += 1

        typo_rate = errors.get("typo_rate", 0.0)
        if rng.random() < typo_rate:
            typo_result = typo_rules.apply_random_typo(transformed, rng)
            if typo_result is not None:
                changes.append(ChangeTrace(
                    rule="typo", before=transformed, after=typo_result, probability=typo_rate,
                    triggered=True, dictionary_version=dictionary_version,
                    rule_engine_version=RULE_ENGINE_VERSION, seed=seed, fallback_level=0,
                ))
                transformed = typo_result
                error_count += 1

        output_parts.append(transformed)

    output_parts.append(naturalized[last_end:])
    result_text = "".join(output_parts)

    known_word_rate = errors.get("known_word_error_rate", 0.0)
    before_lexical = result_text
    result_text = lexical_rules.apply_dictionary(result_text, lexical_entries, style, known_word_rate, rng)
    result_text = lexical_rules.apply_known_mistakes(result_text, known_mistakes, known_word_rate, rng)
    if result_text != before_lexical:
        error_count += 1

    punctuation_rate = errors.get("punctuation_error_rate", 0.0)
    result_text = punctuation_rules.drop_trailing_period(result_text, rng, punctuation_rate)
    result_text = punctuation_rules.drop_oxford_comma_before_baglac(result_text, rng, punctuation_rate)
    if persona.get("allow", {}).get("lowercase_sentence_start"):
        result_text = punctuation_rules.lowercase_sentence_start(result_text, rng, punctuation_rate)

    word_count = max(1, len(text.split()))
    qg_result = quality_gate_module.evaluate(text, result_text, error_count, word_count)

    return HumanizeResult(
        original=text,
        output=result_text,
        style=style,
        changes=changes,
        quality_gate=qg_result,
        seed=seed,
    )
