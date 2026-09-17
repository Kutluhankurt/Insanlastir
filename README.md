# Turkish Human Writing Naturalizer

[![CI](https://github.com/Kutluhankurt/turkish-humanizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Kutluhankurt/turkish-humanizer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Türkçe LLM çıktılarını, anlamı koruyarak daha doğal ve insan yazımına yakın
hale getiren kural tabanlı bir humanizer.

Tasarım dokümanı: [`turkish_human_writing_naturalizer_plan.md`](turkish_human_writing_naturalizer_plan.md).

Bu depo, plandaki **Faz 1 — Rule Engine** kapsamını gerçekleyen ilk çalışan
iskeleti içerir.

## Kurulum

```bash
git clone https://github.com/Kutluhankurt/turkish-humanizer.git
cd turkish-humanizer
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

`pip install -e .` hem bağımlılıkları kurar hem de `turkish-humanizer` komutunu
PATH'e ekler. Yalnızca bağımlılıkları kurmak isterseniz `pip install -r requirements.txt`
yeterlidir.

### Docker ile

```bash
docker compose up --build
# POST http://127.0.0.1:8000/humanize
```

## Kullanım

### Komut satırı

```bash
turkish-humanizer "Yarın tekrar kontrol edeceğim." --style whatsapp --seed 3
# çıktı: Yarın tekrar kontrol edicem.

# stdin'den:
echo "Kontroller gerçekleştirilmiştir." | turkish-humanizer --style technical_engineer

# debug trace ile JSON çıktı:
turkish-humanizer "Her şeyi gözden geçireceğim." --style whatsapp --json
```

Kurulum yapmadan da çalıştırılabilir: `python -m app.cli "..." --style whatsapp`

### API

```bash
.venv/bin/uvicorn app.main:app --reload
# POST http://127.0.0.1:8000/humanize
# Etkileşimli dokümantasyon: http://127.0.0.1:8000/docs
```

Örnek istek:

```bash
curl -X POST http://127.0.0.1:8000/humanize \
  -H "Content-Type: application/json" \
  -d '{"text": "Yarın tekrar kontrol edeceğim.", "style": "whatsapp", "seed": 3, "error_level": 3}'
```

## Testler

```bash
.venv/bin/python -m pytest tests/ -v
```

CI, her push/PR'da Python 3.8 ve 3.11 üzerinde test paketini çalıştırır
(bkz. `.github/workflows/ci.yml`).

## Faz 1 kapsamı: ne var, ne yok

**Çalışıyor:**
- Yüklem çekim dönüşümleri, gerçek Türkçe ünlü uyumuyla (`-yorum→-yom`,
  `-acağım/-eceğim→-ıcam/-icem/-ucam/-ücem`, ünlü uyumu koda gömülü) —
  `app/error_engine/predicate_rules.py`
- Human Error Dictionary (çok varyantlı) + known_mistakes (tek varyantlı) —
  `data/human_error_dictionary.json`, `data/known_mistakes.json`
- Typo engine (silme, tekrarlama, komşu tuş) — `app/error_engine/typo_rules.py`
- Noktalama düzensizlikleri — `app/error_engine/punctuation_rules.py`
- Protected tokens (URL, IP, ID, versiyon, tarih, para birimi, sık İngilizce
  teknik terimler) — `app/guardian/protected_tokens.py`
- Negation guard (sonek tabanlı, morfoloji olmadan) — `app/guardian/negation.py`
- Quality Gate (negation + protected token + sayı + hata yoğunluğu) —
  `app/guardian/quality_gate.py`
- Seed tabanlı reproducibility, dictionary/rule engine versiyonlama, debug
  trace (plan Bölüm 53) — `app/error_engine/engine.py`
- FastAPI `/humanize` endpoint (plan Bölüm 29) — `app/api/humanize.py`

**Henüz stub / sonraki fazlar:**
- `app/naturalizer/` — LLM tabanlı stil dönüşümü şu an no-op (Faz 2)
- `app/morphology/analyzer.py`, `dependency.py` — gerçek Zemberek/Stanza
  entegrasyonu yok; basit sonek heuristiği kullanılıyor (plan Bölüm 50,
  Faz 1 sonrası öncelikli iş)
- `app/guardian/semantic.py` — embedding tabanlı benzerlik yok (Faz 3)
- `de/da/ki/mi` bağlaç/ek ayrımı motoru (plan Bölüm 9) henüz eklenmedi;
  gerçek morfolojik analiz olmadan güvenilir yapılamayacağı için Bölüm 50
  entegrasyonuna bağlı bırakıldı
- `scripts/build_dataset.py`, `scripts/evaluate.py` — çalışan iskelet var,
  gerçek anotasyon/kalite süreci Faz 4 işi

## Sıradaki adım

Plan Bölüm 46'daki sıraya göre: Zemberek/Stanza entegrasyonu (Bölüm 50) ve
`de/da/ki/mi` motoru (Bölüm 9), ardından Naturalizer LLM katmanı (Faz 2).

## Lisans

[MIT](LICENSE)
