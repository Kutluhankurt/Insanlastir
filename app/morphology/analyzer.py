"""Morfolojik analiz katmanı.

STUB: Bölüm 50'de karara bağlanan hibrit stack (Zemberek + Stanza/Trankit)
henüz entegre edilmedi. Bu modül, gerçek analiz gelene kadar Human Error
Engine'in çalışabilmesi için basit sözlük/ek tabanlı bir yaklaşım sunar.

Zemberek entegrasyonu eklendiğinde ``analyze()`` fonksiyonu JPype köprüsü
üzerinden gerçek morfolojik ayrıştırma ve de/da/ki/mi disambiguation
sonucu dönecek şekilde değiştirilmeli; confidence skoru gerçek analiz
güveninden gelmeli (bkz. Bölüm 51 - fallback stratejisi).
"""
from dataclasses import dataclass
from typing import Optional

# Sık kullanılan yüklem/fiil çekim ekleri - tam POS tagger gelene kadar
# "bu kelime muhtemelen bir yüklem" heuristiği için kullanılır.
_VERB_SUFFIX_HINTS = (
    "yorum", "yoruz", "yorsun", "yorsunuz", "yor",
    "acağım", "eceğim", "acağız", "eceğiz",
    "dı", "di", "du", "dü", "tı", "ti", "tu", "tü",
    "mış", "miş", "muş", "müş",
    "malı", "meli",
)


@dataclass
class MorphResult:
    token: str
    is_likely_predicate: bool
    confidence: float


def analyze(token: str) -> MorphResult:
    """Tek bir kelime için basitleştirilmiş morfolojik ipucu döner.

    Gerçek bir morfolojik analiz DEĞİLDİR; yalnızca ek kalıplarına bakarak
    kaba bir tahmin yapar. Düşük confidence, Bölüm 51'deki eşik mekanizması
    ile dönüşümün atlanmasını sağlar.
    """
    lower = token.lower()
    is_predicate = lower.endswith(_VERB_SUFFIX_HINTS)
    # Heuristik olduğu için confidence kasıtlı olarak orta seviyede tutulur.
    confidence = 0.75 if is_predicate else 0.5
    return MorphResult(token=token, is_likely_predicate=is_predicate, confidence=confidence)
