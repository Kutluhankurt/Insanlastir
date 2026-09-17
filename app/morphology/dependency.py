"""Dependency parsing katmanı (Bölüm 50).

Stanza (Stanford NLP) ile Türkçe UD (IMST treebank) dependency parsing.
`stanza` kuruluysa (`pip install -e ".[dependency]"`) gerçek ROOT
ilişkisiyle bir cümlenin ana yüklemini bulur; kurulu değilse (varsayılan)
boş liste döner ve çağıran taraf eski davranışına (tüm yüklem adaylarını
eşit ağırlıklı görme) geri düşer.

Neden negation guard'a (Bölüm 18) bağlanmadı: negation guard orijinal
metinle humanize edilmiş metni KARŞILAŞTIRIYOR (cross-text). Naturalizer
kelime sırasını/cümle bölünmesini değiştirebildiği için iki farklı parse
ağacını hizalamak kırılgan bir problemdir - mevcut kelime bazlı sayım
(bkz. `app/guardian/negation.py`) bu karşılaştırma için daha sağlam bir
temel sağlıyor. Dependency parse, TEK bir metin üzerinde (Human Error
Engine'in ROOT/predicate tespiti gibi, aşağıdaki `find_root_words`)
güvenle kullanılabilir; cross-text hizalama gerektirmez.

Ağır bağımlılık (torch tabanlı) ve ilk çalıştırmada model indirmesi
gerektirdiği için opt-in tutuldu - Faz 1/2/3'ün kurulumunu bozmasın diye.
"""
import sys
from dataclasses import dataclass
from typing import List

_LANG = "tr"
_PROCESSORS = "tokenize,pos,lemma,depparse"
_pipeline = None


@dataclass
class ParsedWord:
    text: str
    lemma: str
    upos: str
    head: int  # 1-indexli; 0 = ROOT'a bağlı (yani bu kelime ROOT'tur)
    deprel: str


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    import stanza

    try:
        _pipeline = stanza.Pipeline(_LANG, processors=_PROCESSORS, verbose=False)
    except Exception:
        print(f"[dependency] '{_LANG}' modeli indiriliyor (ilk çalıştırma)...", file=sys.stderr)
        stanza.download(_LANG, verbose=False)
        _pipeline = stanza.Pipeline(_LANG, processors=_PROCESSORS, verbose=False)
    return _pipeline


def parse(text: str) -> List[List[ParsedWord]]:
    """Metni cümlelere ayırıp her cümle için kelime listesi döner.

    `stanza` kurulu değilse veya parse başarısız olursa boş liste döner
    (Bölüm 51 fallback stratejisi - sessizce atla, pipeline'ı çökertme).
    """
    try:
        nlp = _get_pipeline()
    except ImportError:
        return []
    except Exception as exc:
        print(f"[dependency] parse başarısız: {exc}", file=sys.stderr)
        return []

    try:
        doc = nlp(text)
    except Exception as exc:
        print(f"[dependency] parse başarısız: {exc}", file=sys.stderr)
        return []

    sentences = []
    for sent in doc.sentences:
        words = [
            ParsedWord(
                text=w.text,
                lemma=w.lemma or w.text,
                upos=w.upos or "",
                head=w.head,
                deprel=w.deprel or "",
            )
            for w in sent.words
        ]
        sentences.append(words)
    return sentences


def find_root_words(text: str) -> List[str]:
    """Her cümlenin ROOT'a bağlı (ana yüklem) kelimesinin yüzey formunu döner.

    `stanza` kurulu değilse boş liste döner; çağıran taraf bunu "predicate
    boost uygulanamıyor" olarak yorumlamalı, hata olarak değil.
    """
    roots = []
    for words in parse(text):
        for w in words:
            if w.deprel == "root":
                roots.append(w.text)
                break
    return roots
