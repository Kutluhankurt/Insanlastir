"""Dependency parsing katmanı.

STUB: Bölüm 50'de Stanza/Trankit ile Türkçe UD (IMST) dependency parsing
kararı alındı ama entegrasyon Faz 1 kapsamı dışında. Bu modül, negation
guard (Bölüm 18) ve predicate tespiti (Bölüm 5) gerçek parser'a
bağlanana kadar cümleyi bölmeden geçiren bir no-op sağlar.
"""
from typing import List


def find_predicate_indices(tokens: List[str]) -> List[int]:
    """Cümledeki muhtemel yüklem token indekslerini döner.

    Gerçek bağımlılık ayrıştırması yerine Türkçe'de yüklemin genellikle
    cümle sonunda olması varsayımına dayanır. Bölüm 50 entegrasyonu
    sonrası gerçek ROOT ilişkisiyle değiştirilmelidir.
    """
    if not tokens:
        return []
    return [len(tokens) - 1]
