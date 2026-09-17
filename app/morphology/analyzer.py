"""Morfolojik analiz katmanı (Bölüm 50).

Bölüm 50'de Zemberek + Stanza/Trankit hibrit stack önerilmişti. Gerçek
entegrasyon denemesinde şu bulgular ortaya çıktı:

- Zemberek-NLP artık Maven Central'da YOK (JCenter/Bintray kapandığından
  beri) ve GitHub'da da önceden derlenmiş jar yayınlamıyor; kullanmak
  için kaynak koddan Maven ile derlemek gerekiyor. Bu, "GitHub repo'dan
  doğrudan kullanılabilir" hedefiyle çelişiyor (JVM + çok modüllü Maven
  build + Java toolchain gereksinimi).
- Bunun yerine ``zeyrek`` (Zemberek morfolojisinin saf Python portu,
  PyPI'da) kullanıldı. 0.1.3 sürümü Python 3.8'de `set[X]` generic alias
  sözdizimi (PEP 585, 3.9+) nedeniyle çöküyor; bu yüzden ``zeyrek==0.1.2``
  sabitlendi (bkz. requirements.txt / pyproject.toml).
- zeyrek, Zemberek'in istatistiksel disambiguator'ını İÇERMİYOR: yalnızca
  aday parse listesi döner, bağlama göre en olası olanı SEÇMEZ. Bu yüzden
  "kelime için X POS'u olası mı" sorusuna cevap verebiliyoruz ama "bu
  cümlede kesin doğru okuma budur" diyemiyoruz. Bölüm 9'daki de/da/ki/mi
  motoru ve Bölüm 18'deki negation guard bu sınırlamayı göz önünde
  bulundurarak (aday listesinde ilgili POS/morfem VARSA olası say)
  tasarlandı.

Stanza/Trankit (dependency parsing) entegrasyonu henüz yapılmadı;
``dependency.py`` hâlâ no-op stub'tır.
"""
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Set

_analyzer = None
_nltk_data_ready = False


@dataclass
class MorphResult:
    token: str
    is_likely_predicate: bool
    confidence: float


def _get_zeyrek_analyzer():
    """zeyrek.MorphAnalyzer singleton'ını tembel şekilde oluşturur.

    İlk çağrıda ~3-4 saniye sürer (sözlük yükleme); süreç ömrü boyunca
    bir kez oluşturulur. NLTK'nın 'punkt_tab' verisi eksikse otomatik
    indirir (Bölüm - "doğrudan kullanılabilir" hedefiyle uyumlu, manuel
    kurulum adımı gerektirmez).
    """
    global _analyzer, _nltk_data_ready
    if _analyzer is not None:
        return _analyzer

    import zeyrek

    _analyzer = zeyrek.MorphAnalyzer()
    if not _nltk_data_ready:
        try:
            _analyzer.analyze("deneme")
        except LookupError:
            import nltk

            print("[morphology] NLTK 'punkt_tab' verisi indiriliyor (ilk çalıştırma)...", file=sys.stderr)
            nltk.download("punkt_tab", quiet=True)
        _nltk_data_ready = True
    return _analyzer


@lru_cache(maxsize=4096)
def analyze_word(word: str):
    """Tek bir kelime için zeyrek'ten ham parse aday listesini döner.

    Kelime tanınmıyorsa (OOV) boş liste döner.
    """
    try:
        analyzer = _get_zeyrek_analyzer()
    except Exception:
        return []
    results = analyzer.analyze(word)
    if not results or not results[0]:
        return []
    parses = results[0]
    if len(parses) == 1 and parses[0].pos == "Unk":
        return []
    return parses


def pos_tags(word: str) -> Set[str]:
    return {p.pos for p in analyze_word(word)}


def is_predicate_like(word: str) -> bool:
    """Kelimenin en az bir olası okumasında fiil (Verb) olup olmadığı."""
    return "Verb" in pos_tags(word)


def has_negation(word: str) -> bool:
    """En az bir olası parse'da 'Neg' morfemi var mı.

    Kasıtlı olarak liberal: disambiguation yapılamadığından, olumsuzluk
    OLASI ise (kesin değilse bile) True döner. Bölüm 18'deki negation
    guard için amaç kaçırılan gerçek bir olumsuzluğu yakalamaktır; bu
    yönde hata yapmak (false positive), ters yönde hata yapmaktan
    (gerçek bir olumsuzluk kaybını kaçırmak) çok daha güvenlidir.
    """
    return any("Neg" in p.morphemes for p in analyze_word(word))


def is_known_word(word: str) -> bool:
    return len(analyze_word(word)) > 0


def analyze(token: str) -> MorphResult:
    """Geriye dönük uyumlu özet sonuç (bkz. eski heuristik sürüm)."""
    known = is_known_word(token)
    confidence = 0.9 if known else 0.2
    return MorphResult(token=token, is_likely_predicate=is_predicate_like(token), confidence=confidence)
