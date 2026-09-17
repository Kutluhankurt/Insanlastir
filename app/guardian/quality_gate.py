"""Quality Gate (Bölüm 20, Bölüm 22 error budget).

Faz 1'de semantic similarity (Bölüm 19) henüz aktif olmadığından bu
kapı; negation, protected token ve error budget kontrollerine dayanır.
Semantic Guardian'ın embedding kısmı Faz 3'te eklendiğinde
`semantic_score` alanı da zorunlu hale getirilmelidir.
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.guardian.negation import negation_preserved
from app.guardian.protected_tokens import find_protected_spans
from app.guardian.semantic import cosine_similarity

_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")


@dataclass
class QualityGateResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)
    semantic_score: Optional[float] = None


def _numbers_preserved(original: str, humanized: str) -> bool:
    return sorted(_NUMBER_RE.findall(original)) == sorted(_NUMBER_RE.findall(humanized))


def _protected_tokens_preserved(original: str, humanized: str) -> bool:
    values = sorted(span.value for span in find_protected_spans(original))
    for value in values:
        if value not in humanized:
            return False
    return True


def evaluate(
    original: str,
    humanized: str,
    error_count: int,
    word_count: int,
    max_errors_per_100_words: float = 5,
) -> QualityGateResult:
    reasons: List[str] = []

    if not negation_preserved(original, humanized):
        reasons.append("negation_violation")

    if not _numbers_preserved(original, humanized):
        reasons.append("number_mismatch")

    if not _protected_tokens_preserved(original, humanized):
        reasons.append("protected_token_violation")

    if word_count > 0:
        density = (error_count / word_count) * 100
        if density > max_errors_per_100_words:
            reasons.append("error_density_exceeded")

    semantic_score = cosine_similarity(original, humanized)
    if semantic_score is not None and semantic_score < 0.90:
        reasons.append("semantic_similarity_low")

    return QualityGateResult(passed=len(reasons) == 0, reasons=reasons, semantic_score=semantic_score)
