"""Turkish Naturalizer (Bölüm 3.1, Faz 2).

Claude API (Anthropic) ile LLM tabanlı stil dönüşümü yapar: fazla resmi/
yapay LLM kalıplarını, anlamı koruyarak daha doğal Türkçeye yaklaştırır.

Güvenli varsayılan: `ANTHROPIC_API_KEY` ortam değişkeni ayarlanmamışsa
(veya `anthropic` paketi kurulu değilse) metni DEĞİŞTİRMEDEN döndürür.
Böylece hiçbir maliyet oluşturmadan ve hiçbir ek kurulum gerektirmeden
Faz 1 rule engine tek başına çalışmaya devam eder - LLM katmanı tamamen
opt-in'dir (`pip install -e ".[llm]"` + kendi API anahtarını ayarlamak).
"""
import os
import sys

from app.naturalizer.prompts import build_system_prompt, build_user_prompt

_MODEL = "claude-opus-5"
_MAX_TOKENS = 4096


def naturalize(text: str, style: str) -> str:
    if not text.strip():
        return text
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return text

    try:
        return _call_llm(text, style)
    except Exception as exc:
        # Bölüm 51 fallback felsefesi: Naturalizer başarısız olursa
        # orijinal metni değiştirmeden geçir, pipeline'ın tamamını
        # çökertme.
        print(f"[naturalizer] LLM çağrısı başarısız oldu, orijinal metin kullanılıyor: {exc}", file=sys.stderr)
        return text


def _call_llm(text: str, style: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=build_system_prompt(style),
        messages=[{"role": "user", "content": build_user_prompt(text)}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text.strip()
    return text
