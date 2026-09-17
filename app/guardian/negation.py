"""Kritik Negation Guard (Bölüm 18).

Olumsuzluk yapılarının orijinal ve humanize edilmiş metin arasında
korunup korunmadığını kontrol eder.

Tam morfolojik analiz (Bölüm 50) gelmeden önce genel bir "-ma-/-me-"
regex'i denenmişti ancak bu, "-meli" (gereklilik: "yapmalı") gibi
olumsuzlukla ilgisi olmayan eklerle karışıyordu (ör. "güncellenmeli"
yanlışlıkla olumsuz sayılıyordu). Bunun yerine, sözcük SONUNDA
görülen ve gerçekten olumsuzluk taşıyan sonek/kelime listesine dayanan
daha dar ama güvenilir bir kontrol kullanılıyor. Bu liste eksiksiz
değildir (Bölüm 50 entegrasyonu ile morfolojik temelli hale
getirilmelidir) ama yanlış pozitif üretmemeyi önceliklendirir.
"""
from typing import List

from app.morphology.tokenizer import tokenize

# Sözcük SONUNDA aranan olumsuzluk belirteçleri. "-meli/-malı" gibi salt
# gereklilik ekleriyle karışmaması için olumsuzluk+gereklilik birleşik
# hallerini (mamalı/memeli) ayrıca listeliyoruz.
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


def count_negation_markers(text: str) -> int:
    words: List[str] = [t.text.lower() for t in tokenize(text) if t.is_word]
    return sum(1 for word in words if word.endswith(_NEGATION_SUFFIXES))


def negation_preserved(original: str, humanized: str) -> bool:
    """Kaba kontrol: olumsuzluk belirteç sayısı azalmamalı.

    Bu tam bir semantik kontrol değildir (bkz. Bölüm 19 - hybrid
    validation); yalnızca bariz bir "değil" / "yok" / "-mamalı" kaybını
    yakalamak için hızlı bir ilk savunma hattıdır.
    """
    return count_negation_markers(original) <= count_negation_markers(humanized)
