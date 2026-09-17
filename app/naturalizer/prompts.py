"""Faz 2 (Bölüm 3.1, Bölüm 41) - LLM tabanlı stil dönüşümü için prompt şablonları."""

STYLE_DESCRIPTIONS = {
    "technical_engineer": "teknik bir mühendisin iş arkadaşına yazdığı, resmi olmayan ama düzgün rapor/mesaj üslubu",
    "casual": "gündelik iş yazışması, samimi ama saygılı üslup",
    "whatsapp": "WhatsApp'ta arkadaşlar arası yazışma gibi rahat, kısa cümleli üslup",
}

SYSTEM_PROMPT_TEMPLATE = """\
Sen bir Türkçe metin doğallaştırma asistanısın. Görevin, verilen metni \
anlamını KESİNLİKLE değiştirmeden, fazla resmi/yapay LLM kalıplarından \
arındırıp {style_description} üslubuna yaklaştırmaktır.

Kurallar:
- Sayıları, ID'leri, URL'leri, tarihleri ve teknik terimleri değiştirme.
- Olumsuzluk yapısını (değil / yok / -ma / -me) asla tersine çevirme.
- Anlamı koru, yalnızca üslubu ve cümle yapısını doğallaştır.
- Yazım hatası veya konuşma dili ekleme (örn. "geliyom", "birşey"); bu ayrı \
bir katmanın işi, senin görevin değil.
- Yalnızca doğallaştırılmış metni döndür. Açıklama, önsöz, tırnak işareti \
veya "İşte doğallaştırılmış metin:" gibi ekler ekleme.
"""

USER_PROMPT_TEMPLATE = """\
Metin:
{text}
"""


def build_system_prompt(style: str) -> str:
    description = STYLE_DESCRIPTIONS.get(style, style)
    return SYSTEM_PROMPT_TEMPLATE.format(style_description=description)


def build_user_prompt(text: str) -> str:
    return USER_PROMPT_TEMPLATE.format(text=text)
