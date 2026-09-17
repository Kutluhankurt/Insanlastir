"""Kritik Negation Guard (Bölüm 18).

Olumsuzluk yapılarının orijinal ve humanize edilmiş metin arasında
korunup korunmadığını kontrol eder.

Bölüm 50 entegrasyonu ile artık birincil kaynak zeyrek'in morfolojik
analizi: bir kelime tanınıyorsa (OOV değilse) 'Neg' morfemi arandığı
için "-meli" (gereklilik) gibi yanıltıcı yüzeysel benzerliklere
düşmüyor. Kelime tanınmıyorsa (ör. Human Error Engine'in ürettiği
"görülmüyo" gibi konuşma dili biçimleri; bkz. Bölüm 51 - fallback
stratejisi) eski sonek tabanlı sözlük listesine düşülür.
"""
from typing import List

from app.morphology import analyzer
from app.morphology.tokenizer import tokenize

# Fallback: zeyrek'in OOV bıraktığı (ör. Human Error Engine'in ürettiği
# konuşma dili biçimleri) kelimeler için sözcük SONUNDA aranan
# olumsuzluk belirteçleri.
_NEGATION_SUFFIXES = (
    "değildir", "değil", "yok", "hariç",
    "mamalıdır", "memelidir", "mamalı", "memeli",
    "mayacaktır", "meyecektir", "mayacak", "meyecek",
    "mamak", "memek",
    "madan", "meden",
    "mıyor", "miyor", "muyor", "müyor",
    "madı", "medi", "madım", "medim", "madık", "medik",
    "maz", "mez",
)


def _word_has_negation(word: str) -> bool:
    if analyzer.is_known_word(word):
        return analyzer.has_negation(word)
    lower = word.lower()
    return lower.endswith(_NEGATION_SUFFIXES)


def count_negation_markers(text: str) -> int:
    words: List[str] = [t.text for t in tokenize(text) if t.is_word]
    return sum(1 for word in words if _word_has_negation(word))


def negation_preserved(original: str, humanized: str) -> bool:
    """Kaba kontrol: olumsuzluk belirteç sayısı azalmamalı.

    Bu tam bir semantik kontrol değildir (bkz. Bölüm 19 - hybrid
    validation); yalnızca bariz bir "değil" / "yok" / "-mamalı" kaybını
    yakalamak için hızlı bir ilk savunma hattıdır.
    """
    return count_negation_markers(original) <= count_negation_markers(humanized)
