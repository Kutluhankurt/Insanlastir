"""Basit boşluk/noktalama tabanlı tokenizer.

Faz 1'de tam bir Türkçe tokenizer yerine kelime sınırlarını bulan hafif bir
uygulama kullanılıyor. Bölüm 50'deki Zemberek/Stanza entegrasyonu geldiğinde
bu modül onların tokenizer'ı ile değiştirilecek.
"""
import re
from typing import List, NamedTuple


class Token(NamedTuple):
    text: str
    start: int
    end: int
    is_word: bool


_TOKEN_RE = re.compile(r"[^\W\d_]+|\d+|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> List[Token]:
    tokens = []
    for match in _TOKEN_RE.finditer(text):
        value = match.group(0)
        is_word = value.isalpha()
        tokens.append(Token(value, match.start(), match.end(), is_word))
    return tokens
