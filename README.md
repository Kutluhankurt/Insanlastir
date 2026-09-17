# İnsanlaştır

**Türkçe LLM çıktılarını, anlamı koruyarak gerçek insan yazımına yaklaştıran kural tabanlı motor.**

[![CI](https://github.com/Kutluhankurt/Insanlastir/actions/workflows/ci.yml/badge.svg)](https://github.com/Kutluhankurt/Insanlastir/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](pyproject.toml)

---

## Neden?

Büyük dil modelleri çok düzgün yazar — çok dengeli cümleler, çok tutarlı
noktalama, hiç "gevşeme" yok. Gerçek insanlar öyle yazmaz. İnsanlaştır,
LLM çıktısının üzerine çalışan bir katman: **anlamı bozmadan**, Türkçe'ye
özgü yüklem çekimlerini, `de/da/ki/mi` bitişmelerini ve bilinen yazım
alışkanlıklarını kullanarak metni gerçek bir insanın yazdığı gibi
gösterir.

Rastgele karakter bozan bir "typo generator" değildir — Türkçe ünlü
uyumunu bilen, morfolojik analiz kullanan ve sayı/ID/URL gibi kritik
verileri asla değiştirmeyen kontrollü bir sistemdir.

```text
GİRİŞ:   Ben de yarın tekrar kontrol edeceğim.
ÇIKIŞ:   Bende yarın tekrar kontrol edicem.

GİRİŞ:   Öyle ki herkes bunu biliyor, geliyor musun?
ÇIKIŞ:   Öyleki herkes bunu biliyor, geliyormusun?

GİRİŞ:   Cihaz 4B3338E8, Engine v1.4.2 üzerinde çalışıyor ve yarın tekrar kontrol edeceğim.
ÇIKIŞ:   Cihaz 4B3338E8, Engine v1.4.2 üzerinde çalışıyor ve yarın tekrar kontrol edicem.
         (device ID ve versiyon numarası dokunulmadan kalır)
```

*(`--style whatsapp --seed 0` ile birebir tekrarlanabilir.)*

Tasarımın tamamı için: [`turkish_human_writing_naturalizer_plan.md`](turkish_human_writing_naturalizer_plan.md) (53 bölümlük teknik mimari + ürün planı).

## Özellikler

- 🗣️ **Gerçek ünlü uyumu** — `geliyorum→geliyom`, `yapacağım→yapıcam`, `olacağım→olucam` (dar ünlü + ikinci ünlü uyumu koda gömülü, düz `string.replace()` değil)
- 🔗 **de/da/ki/mi motoru** — standalone bağlaç/soru ekini morfolojik olarak doğrulayıp önceki kelimeyle bitiştirir; `evde` gibi ek olan durumlara asla dokunmaz
- 🧠 **Gerçek morfolojik analiz** — [zeyrek](https://pypi.org/project/zeyrek/) ile POS/lemma/morfem analizi (JVM gerekmez)
- 🌳 **Opsiyonel dependency parsing** — Stanza ile cümlenin ana yüklemini (ROOT) bulup ona daha yüksek öncelik verir
- 🛡️ **Quality Gate** — sayılar, ID'ler, URL'ler, olumsuzluk yapıları hiçbir zaman değişmez; anlam bozulursa çıktı reddedilir
- 🎭 **Persona sistemi** — `technical_engineer`, `casual`, `whatsapp` gibi stiller, her biri farklı hata dağılımına sahip
- 🎲 **Seed tabanlı reproducibility** — aynı girdi + aynı seed = aynı çıktı, test edilebilir ve hata ayıklanabilir
- 🤖 **Opsiyonel LLM stil katmanı** — Claude API ile fazla resmi ifadeleri doğallaştırma (opt-in, varsayılan kapalı/ücretsiz)
- 📊 **Opsiyonel embedding tabanlı anlam kontrolü** — orijinal ve humanize edilmiş metin arasında cosine similarity (opt-in)

## Hızlı Başlangıç

```bash
git clone https://github.com/Kutluhankurt/Insanlastir.git
cd Insanlastir
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .

.venv/bin/insanlastir "Ben de yarın tekrar kontrol edeceğim." --style whatsapp --seed 0
# -> Bende yarın tekrar kontrol edicem.
```

`pip install -e .` hem bağımlılıkları kurar hem de `insanlastir` komutunu
PATH'e ekler. Yalnızca bağımlılıkları kurmak isterseniz
`pip install -r requirements.txt` yeterlidir.

> İlk çalıştırmada morfolojik analiz kütüphanesi (zeyrek) ~4 saniye süren
> bir sözlük yüklemesi yapar ve gerekiyorsa küçük bir NLTK veri dosyasını
> (`punkt_tab`) otomatik indirir. Bu bir defalık/süreç başına maliyettir.

### Docker ile

```bash
docker compose up --build
# POST http://127.0.0.1:8000/humanize
```

## Kullanım

### Komut satırı

```bash
insanlastir "Ben de yarın tekrar kontrol edeceğim." --style whatsapp --seed 0

# stdin'den:
echo "Kontroller gerçekleştirilmiştir." | insanlastir --style technical_engineer

# debug trace ile JSON çıktı:
insanlastir "Her şeyi gözden geçireceğim." --style whatsapp --json
```

Kurulum yapmadan da çalıştırılabilir: `python -m app.cli "..." --style whatsapp`

### API

```bash
.venv/bin/uvicorn app.main:app --reload
# POST http://127.0.0.1:8000/humanize
# Etkileşimli dokümantasyon: http://127.0.0.1:8000/docs
```

```bash
curl -X POST http://127.0.0.1:8000/humanize \
  -H "Content-Type: application/json" \
  -d '{"text": "Yarın tekrar kontrol edeceğim.", "style": "whatsapp", "seed": 3, "error_level": 3}'
```

## Opsiyonel katmanlar (opt-in)

Hepsi varsayılan olarak **kapalı**: kurulu değillerse sessizce no-op'a
düşerler, pipeline hiçbir zaman çökmez.

| Katman | Ne yapar | Nasıl açılır | Maliyet |
|---|---|---|---|
| **Naturalizer** (Faz 2) | Claude API (`claude-opus-5`) ile fazla resmi/yapay ifadeleri doğallaştırır | `pip install -e ".[llm]"` + `export ANTHROPIC_API_KEY=...` | Ücretli (kendi API anahtarınız) |
| **Semantic Guardian** (Faz 3) | Çok dilli embedding (`multilingual-e5-small`) ile anlam benzerliği kontrolü | `pip install -e ".[semantic]"` | Ücretsiz, yerel — ~470MB model indirir |
| **Dependency Parsing** | Stanza (Türkçe UD) ile cümlenin ana yüklemini (ROOT) bulup öncelik verir | `pip install -e ".[dependency]"` | Ücretsiz, yerel — ağır bağımlılık (torch) |

## Mimari

```text
LLM Output
    ↓
Turkish Naturalizer      (opt-in, Claude API)
    ↓
de/da/ki/mi Motoru       (morfolojik doğrulama ile bitiştirme)
    ↓
Human Error Engine       (yüklem, sözlük, typo, noktalama)
    ↓
Quality Gate             (negation + protected tokens + sayı + anlam)
    ↓
Humanized Output
```

Detaylı mimari, ağırlık formülleri, persona şemaları ve yol haritası:
[`turkish_human_writing_naturalizer_plan.md`](turkish_human_writing_naturalizer_plan.md).

## Kapsam

**Çalışıyor:**
- Yüklem çekim dönüşümleri (ünlü uyumuyla) — `app/error_engine/predicate_rules.py`
- Gerçek morfolojik analiz (zeyrek) — `app/morphology/analyzer.py`
- de/da/ki/mi motoru — `app/error_engine/baglac_rules.py`
- Negation guard (gerçek `Neg` morfemi + fallback) — `app/guardian/negation.py`
- Human Error Dictionary + known mistakes — `data/`
- Typo/noktalama motorları, protected tokens, Quality Gate
- Seed tabanlı reproducibility, debug trace, versiyonlama
- FastAPI `/humanize` endpoint, CLI, Docker
- Naturalizer (opt-in, Claude API), Semantic Guardian (opt-in, embedding), Dependency Parsing (opt-in, Stanza)

**Henüz yok:**
- de/da/ki/mi motoru tam bağlamsal disambiguation yapmıyor (zeyrek'te istatistiksel disambiguator yok)
- Gerçek dataset (Faz 4) ve A/B değerlendirmesi (Bölüm 38) — insan verisi/anotasyon gerektiriyor

## Testler

```bash
.venv/bin/python -m pytest tests/ -v
```

CI, her push/PR'da Python 3.8 ve 3.11 üzerinde (opt-in katmanlar dahil)
test paketini çalıştırır — bkz. [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Katkıda Bulunma

Issue ve PR'lara açığız. Büyük bir değişiklik öncesi bir issue açıp
tartışmak, gereksiz iş kaybını önler.

## Lisans

[MIT](LICENSE)

---

Faydalı bulduysanız ⭐ bırakmayı unutmayın.
