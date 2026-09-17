"""Ayrı/bitişik yazım için genel yardımcılar (Bölüm 4, compound-spacing).

Bilinen ifadeler (bir şey, her şey, ...) için birincil mekanizma
human_error_dictionary.json'dur (bkz. lexical_rules.py). Bu modül,
sözlükte olmayan iki kelimelik ifadeleri bitiştirmek için genel amaçlı
bir yardımcı sağlar; ileride kural tabanlı genişleme için kullanılabilir.
"""


def merge_two_words(text: str, phrase: str) -> str:
    """"kelime1 kelime2" -> "kelime1kelime2" (yalnızca birebir eşleşmede)."""
    if phrase not in text:
        return text
    merged = phrase.replace(" ", "", 1)
    return text.replace(phrase, merged, 1)
