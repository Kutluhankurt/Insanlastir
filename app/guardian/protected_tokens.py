"""Protected Tokens (Bölüm 16, genişletilmiş Bölüm 51).

Human Error Engine bu span'lara asla dokunmamalıdır.
"""
import re
from typing import List, NamedTuple

_PATTERNS = [
    re.compile(r"https?://\S+"),                                  # URL
    re.compile(r"[\w.\-]+@[\w.\-]+\.\w+"),                        # email
    re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),                    # IP address
    re.compile(r"\bv?\d+\.\d+(?:\.\d+)?(?:-\w+)?\b"),               # version number
    re.compile(r"\b[A-F0-9]{8}\b"),                                 # device id (hex)
    re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),                    # time
    re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"),               # date
    re.compile(r"%\d+(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?%"),             # percentage
    re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:TL|USD|EUR|\$|₺|€)\b"),     # currency
    re.compile(r"\b\d+(?:[.,]\d+)?\b"),                             # bare number
]

# Bölüm 51: code-switching için basit dil tespiti (fastText/langid'e kadar
# geçici bir önlem). Sık geçen İngilizce teknik terimler otomatik korunur.
_KNOWN_TECH_ENGLISH_WORDS = {
    "container", "docker", "kubernetes", "server", "backend", "frontend",
    "deployment", "pipeline", "commit", "branch", "merge", "endpoint",
    "token", "cache", "queue", "thread", "socket", "firmware", "reboot",
    "update", "config", "log", "logs", "debug", "release",
}


class ProtectedSpan(NamedTuple):
    start: int
    end: int
    value: str
    reason: str


def find_protected_spans(text: str) -> List[ProtectedSpan]:
    spans: List[ProtectedSpan] = []
    for pattern in _PATTERNS:
        for match in pattern.finditer(text):
            spans.append(ProtectedSpan(match.start(), match.end(), match.group(0), pattern.pattern))

    for match in re.finditer(r"[^\W\d_]+", text, re.UNICODE):
        word = match.group(0)
        if word.lower() in _KNOWN_TECH_ENGLISH_WORDS:
            spans.append(ProtectedSpan(match.start(), match.end(), word, "known_tech_english"))

    spans.sort(key=lambda s: s.start)
    return _merge_overlaps(spans)


def _merge_overlaps(spans: List[ProtectedSpan]) -> List[ProtectedSpan]:
    if not spans:
        return []
    merged = [spans[0]]
    for span in spans[1:]:
        last = merged[-1]
        if span.start <= last.end:
            if span.end > last.end:
                merged[-1] = ProtectedSpan(last.start, span.end, last.value, last.reason)
        else:
            merged.append(span)
    return merged


def is_inside_protected(index: int, spans: List[ProtectedSpan]) -> bool:
    return any(span.start <= index < span.end for span in spans)
