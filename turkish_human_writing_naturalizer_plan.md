# Turkish Human Writing Naturalizer
## Türkçe LLM Çıktılarını Daha Doğal ve İnsan Yazımına Yaklaştıran Sistem Tasarımı

**Doküman Türü:** Teknik Mimari + Ürün Planı + MVP Yol Haritası  
**Dil:** Türkçe  
**Ana Hedef:** LLM tarafından üretilmiş fazla düzgün, fazla resmi veya yapay hissi veren Türkçe metinleri; anlamı koruyarak daha doğal, insan yazımına yakın ve kontrollü biçimde kusurlu hale getirmek.

---

# 1. Proje Özeti

Büyük dil modelleri çoğunlukla:

- Dilbilgisel olarak fazla düzgün,
- Cümle yapısı fazla dengeli,
- Noktalama kullanımı fazla tutarlı,
- Aynı resmiyet seviyesini koruyan,
- İnsanların günlük yazım alışkanlıklarından daha temiz

metinler üretir.

Bu proje, LLM çıktısının üzerine çalışan ikinci bir katman geliştirerek Türkçe metni daha doğal insan yazımına yaklaştırmayı amaçlar.

Ancak amaç yalnızca rastgele yazım hatası eklemek değildir.

Asıl hedef:

> **Türkçe için kontrollü, bağlama duyarlı ve morfoloji farkındalığı olan bir Human Writing Naturalizer geliştirmektir.**

Sistem özellikle:

- Yüklem varyasyonları,
- Konuşma diline kayan çekimler,
- Sık yapılan Türkçe yazım hataları,
- `de/da`, `ki`, `mi` kullanımları,
- Ayrı/bitişik yazım hataları,
- Hafif noktalama düzensizlikleri,
- Cümle uzunluğu varyasyonu,
- Kelime seçimi değişiklikleri,
- Kontrollü typo üretimi

üzerinden çalışacaktır.

---

# 2. Temel Fikir

Önerilen ana pipeline:

```text
LLM Output
    ↓
Turkish Naturalizer
    ↓
Morphological Analyzer
    ↓
Human Error Engine
    ↓
Semantic Guardian
    ↓
Quality Gate
    ↓
Humanized Output
```

Her katmanın farklı görevi vardır.

---

# 3. Sistem Bileşenleri

## 3.1 Turkish Naturalizer

Naturalizer katmanının görevi doğrudan yazım hatası yapmak değildir.

Görevi:

- Fazla resmi ifadeleri azaltmak,
- Cümle uzunluklarını çeşitlendirmek,
- Yapay LLM kalıplarını azaltmak,
- Günlük Türkçe kelime tercihlerine yaklaşmak,
- Gereksiz kurumsal ifadeleri sadeleştirmek,
- Cümleleri gerektiğinde bölmek veya birleştirmek.

### Örnek

LLM:

```text
Bu sistem, kullanıcıların işlemlerini daha hızlı gerçekleştirmelerine
olanak tanırken aynı zamanda operasyonel verimliliği artırmayı hedeflemektedir.
```

Naturalizer:

```text
Bu sistem kullanıcıların işlemleri daha hızlı yapmasını sağlıyor.
Bir yandan da operasyon tarafında işleri daha verimli hale getirmeyi hedefliyor.
```

Daha gündelik profil:

```text
Buradaki amaç kullanıcıların işlemleri daha hızlı yapabilmesi.
Operasyon tarafında da işleri biraz daha verimli hale getirmek istiyoruz.
```

---

# 4. Human Error Engine

Projenin en kritik bileşenidir.

Human Error Engine rastgele karakter bozan bir typo generator olmayacaktır.

Bunun yerine:

> **Gerçek Türkçe kullanıcıların hata yapma eğilimlerini modelleyen ağırlıklı ve bağlama duyarlı bir sistem olacaktır.**

Ana hata kategorileri:

```text
Human Error Engine
│
├── Morphological Errors
│   ├── Verb / Predicate transformations
│   ├── Suffix variations
│   ├── de / da
│   ├── ki
│   └── mi
│
├── Lexical Errors
│   ├── bir şey → birşey
│   ├── her şey → herşey
│   ├── yalnız → yanlız
│   ├── yanlış → yalnış
│   └── ...
│
├── Phonetic / Spoken Writing
│   ├── geliyorum → geliyom
│   ├── yapacağım → yapıcam
│   └── geleceğim → gelicem
│
├── Typing Errors
│   ├── character deletion
│   ├── duplication
│   ├── adjacent keyboard key
│   └── missing Turkish character
│
└── Punctuation / Formatting Errors
    ├── missing comma
    ├── missing period
    ├── inconsistent capitalization
    └── extra spacing
```

---

# 5. Neden Yüklemler Daha Önemli?

Türkçede insan yazımını doğal gösteren hataların önemli bir kısmı yüklemlerde veya fiil çekimlerinde görülür.

Örneğin:

```text
geliyorum → geliyom
gidiyorum → gidiyom
bilmiyorum → bilmiyom
istiyorum → istiyom
bekliyorum → bekliyom
gidiyoruz → gidiyoz
yapacağız → yapıcaz
yapacağım → yapıcam
geleceğim → gelicem
edeceğim → edicem
olacağım → olucam
```

Bu nedenle bütün tokenlar eşit hata ihtimaline sahip olmamalıdır.

Önerilen başlangıç ağırlıkları:

```text
Predicate / Verb                ×4.0
Verb containing -yor           ×3.5
Future tense -acak / -ecek     ×3.0
de / da                         ×3.0
ki                              ×2.5
mi                              ×2.5
Known mistake dictionary       ×4.0
Normal noun                    ×0.5
Number                         ×0
URL                            ×0
Device ID                      ×0
Technical identifier           ×0
```

Bu değerler ilk sürümde elle ayarlanabilir, daha sonra gerçek veri üzerinden öğrenilebilir.

---

# 6. Yüklem Dönüşüm Kuralları

Bu dönüşümler düz `string.replace()` ile yapılmamalıdır.

Türkçe ses uyumu ve ek yapısı dikkate alınmalıdır.

## Örnek dönüşüm grupları

### Şimdiki zaman

```text
-yorum  → -yom
-yoruz  → -yoz
```

Örnek:

```text
geliyorum  → geliyom
gidiyorum  → gidiyom
bakıyorum   → bakıyom
bekliyorum  → bekliyom
gidiyoruz   → gidiyoz
```

### Gelecek zaman / birinci şahıs

```text
-acağım / -eceğim
→
-ıcam / -icem / -ucam / -ücem benzeri konuşma varyantları
```

Örnek:

```text
yapacağım   → yapıcam
geleceğim   → gelicem
olacağım    → olucam
edeceğim    → edicem
```

### Gelecek zaman / çoğul

```text
-acağız / -eceğiz
→
-ıcaz / -icez / -ucaz / -ücez benzeri varyantlar
```

Örnek:

```text
yapacağız   → yapıcaz
geleceğiz   → gelicez
olacağız    → olucaz
```

Bu dönüşümlerin her biri bağlama ve stile göre olasılıklı çalışmalıdır.

---

# 7. Sık Yanlış Yazılan Kelimeler Sözlüğü

İkinci önemli yapı bir `Human Error Dictionary` olacaktır.

Örnek:

```yaml
bir şey:
  variants:
    birşey: 0.55
    bişey: 0.30
    bi şey: 0.15

her şey:
  variants:
    herşey: 0.85
    hersey: 0.15

hiçbir:
  variants:
    hiç bir: 1.0

yalnız:
  variants:
    yanlız: 1.0

yanlış:
  variants:
    yalnış: 1.0

herkes:
  variants:
    herkez: 1.0

maalesef:
  variants:
    malesef: 1.0

orijinal:
  variants:
    orjinal: 1.0

sürpriz:
  variants:
    süpriz: 1.0

direkt:
  variants:
    direk: 1.0

değil mi:
  variants:
    dimi: 0.60
    değilmi: 0.40
```

Her varyantın:

- Hata türü,
- Olasılığı,
- Uygulanabileceği stil,
- Resmiyet seviyesi,
- Risk seviyesi

saklanmalıdır.

---

# 8. Önerilen Human Error Dictionary Şeması

```json
{
  "correct": "bir şey",
  "variants": [
    {
      "value": "birşey",
      "weight": 0.55,
      "error_type": "compound_spacing",
      "styles": ["casual", "whatsapp", "social"],
      "semantic_risk": "low"
    },
    {
      "value": "bişey",
      "weight": 0.30,
      "error_type": "phonetic",
      "styles": ["whatsapp", "young_casual"],
      "semantic_risk": "low"
    }
  ]
}
```

---

# 9. `de / da`, `ki`, `mi` Motoru

Bu alan Türkçe Human Error Engine için ayrı ele alınmalıdır.

## Örnekler

```text
ben de geleceğim
↓
bende gelicem
```

```text
biliyor musun
↓
biliyomusun
```

```text
öyle ki
↓
öyleki
```

Ancak burada kör dönüşüm yapılmamalıdır.

Örneğin:

```text
evde
```

kelimesindeki `-de` bulunma halidir.

Buna karşılık:

```text
ben de
```

ifadesindeki `de` bağlaçtır.

Sistem bunları morfolojik olarak ayırt etmelidir.

Önerilen akış:

```text
Token
  ↓
Morphological Parse
  ↓
Suffix or Conjunction?
  ↓
Applicable Error Rule?
  ↓
Probability Check
  ↓
Transformation
```

---

# 10. Morfolojik Analiz

Türkçe eklemeli bir dil olduğu için Human Error Engine'in en önemli teknik gereksinimlerinden biri morfolojik analizdir.

İlk sürümde kullanılabilecek yaklaşım:

```text
Sentence
    ↓
Tokenizer
    ↓
Morphological Analyzer
    ↓
POS Tagger
    ↓
Dependency Parser
    ↓
Predicate Detection
    ↓
Error Candidate Generator
```

Her token için aşağıdaki bilgiler tutulabilir:

```json
{
  "token": "geleceğim",
  "lemma": "gel",
  "pos": "VERB",
  "is_predicate": true,
  "tense": "FUT",
  "person": "1SG",
  "suffixes": ["FUT", "1SG"]
}
```

Bu bilgiler Error Engine'e gönderilir.

---

# 11. Error Susceptibility Score

Her kelimenin hata alma ihtimali farklı olmalıdır.

Önerilen formül:

```text
error_score(token) =
    base_probability
  × pos_weight
  × predicate_weight
  × suffix_weight
  × known_mistake_weight
  × sentence_position_weight
  × persona_weight
  × style_weight
```

Örnek:

```text
"geleceğim"

base_probability        = 0.02
POS_weight              = 2.0
predicate_weight        = 2.0
future_suffix_weight    = 3.0
casual_style_weight     = 1.8

final score ≈ weighted probability
```

Bu skor doğrudan olasılık olmak zorunda değildir.

Normalize edilip candidate ranking için de kullanılabilir.

---

# 12. Typo Engine

Typo Engine ayrı bir alt katman olacaktır.

Ama typo oranı düşük tutulmalıdır.

İnsanlaştırmayı yalnızca typo üzerinden yapmak yapay sonuç üretir.

Desteklenecek typo tipleri:

## Character deletion

```text
aslında → aslnda
```

## Character duplication

```text
merhaba → merhabaa
```

## Adjacent keyboard key

```text
olacak → olacsk
```

## Turkish character normalization

```text
ş → s
ğ → g
ı → i
ö → o
ü → u
ç → c
```

Bu özellikle belirli persona ve platformlarda kullanılmalıdır.

Örneğin masaüstü teknik mail profiline göre Türkçe karakter kaybı çok düşük tutulabilir.

---

# 13. Noktalama Hataları

İnsan yazısında doğal görülebilecek küçük düzensizlikler:

```text
virgül atlama
nokta atlama
cümle başında küçük harf
fazladan boşluk
noktalama öncesi boşluk
gereksiz üç nokta
```

Örnek:

```text
Tamam, kontrol ettim. Şu an sorun görünmüyor.
```

↓

```text
Tamam kontrol ettim, şu an sorun görünmüyor
```

Ancak bütün cümlelerde yapılmamalıdır.

---

# 14. Persona / Style Sistemi

Tek bir Humanizer profili yerine stil kontrollü sistem önerilir.

Örnek profiller:

```text
formal_business
casual_business
technical_engineer
whatsapp
young_casual
social_media
clean_human
slightly_sloppy
```

Her profil farklı hata dağılımına sahip olabilir.

---

# 15. Örnek Profil Konfigürasyonu

## technical_engineer

```yaml
style: technical_engineer

naturalization:
  strength: 0.55

errors:
  typo_rate: 0.003
  punctuation_error_rate: 0.02
  predicate_variation_rate: 0.12
  known_word_error_rate: 0.015

allow:
  casual_verbs: true
  sentence_shortening: true

protect:
  numbers: true
  urls: true
  ids: true
  version_numbers: true
  code: true
  proper_nouns: true
```

## whatsapp

```yaml
style: whatsapp

naturalization:
  strength: 0.85

errors:
  typo_rate: 0.02
  punctuation_error_rate: 0.12
  predicate_variation_rate: 0.35
  known_word_error_rate: 0.08
  phonetic_rate: 0.20

allow:
  abbreviations: true
  spoken_forms: true
  lowercase_sentence_start: true
```

---

# 16. Protected Tokens

Bazı içeriklere Human Error Engine kesinlikle dokunmamalıdır.

Örneğin:

```text
IP address
URL
email
device ID
version number
serial number
date
time
percentage
currency
code
terminal command
file path
```

Örnek regex korumaları:

```regex
\b[A-F0-9]{8}\b
https?://\S+
[\w\.-]+@[\w\.-]+\.\w+
\b\d{1,3}(?:\.\d{1,3}){3}\b
\bv?\d+\.\d+(?:\.\d+)?(?:-\w+)?\b
```

Örnek:

```text
Device ID 4B3338E8, Engine v1.4.2 ve IP 192.168.1.20
```

Bu alanlar değişmemelidir.

---

# 17. Semantic Guardian

Human Error Engine'in ardından mutlaka Semantic Guardian çalışmalıdır.

Amaç:

> İnsanlaştırma sırasında anlamın bozulmadığını doğrulamak.

Kontrol edilmesi gereken kritik noktalar:

- Sayılar değişmiş mi?
- Olumsuzluk kaybolmuş mu?
- `var` → `yok` gibi tersine dönüş olmuş mu?
- `yapacak` → `yapmayacak` olmuş mu?
- Özel isim değişmiş mi?
- Cihaz ID değişmiş mi?
- Tarih değişmiş mi?
- Teknik parametre değişmiş mi?

---

# 18. Kritik Negation Guard

Türkçede özellikle aşağıdaki yapılar korunmalıdır:

```text
-ma / -me
değil
yok
hariç
olmamalı
yapılmamalı
gelmeyecek
çalışmıyor
```

Örneğin:

```text
Cihaz yeniden başlatılmamalıdır.
```

Naturalizer:

```text
Cihaz yeniden başlatılmamalı.
```

Kabul edilebilir.

Ama:

```text
Cihaz yeniden başlatılmalı.
```

kabul edilemez.

Bu yüzden negation tokenları ayrı checksum gibi kontrol edilebilir.

---

# 19. Semantic Similarity

İlk MVP'de embedding tabanlı benzerlik kullanılabilir.

Örnek:

```text
original_embedding
humanized_embedding
        ↓
cosine similarity
```

Threshold örneği:

```text
similarity >= 0.90
```

Ancak tek başına embedding yeterli değildir.

Bu nedenle hybrid validation önerilir:

```text
Semantic Similarity
+
Protected Token Equality
+
Number Equality
+
Negation Check
+
Named Entity Check
```

---

# 20. Quality Gate

Final çıktı aşağıdaki kontrollerden geçmelidir:

```text
1. Semantic similarity passed?
2. Protected tokens preserved?
3. Numbers preserved?
4. Negation preserved?
5. Error density acceptable?
6. Too many errors in one sentence?
7. Same error repeated excessively?
8. Output still readable?
```

Başarısızsa:

```text
Retry with lower error intensity
```

---

# 21. Hata Yoğunluğu

İnsanlaştırma seviyesi kullanıcı tarafından ayarlanabilir.

Önerilen seviye sistemi:

## Level 0 — Clean

```text
Sadece doğal cümle yapısı.
Yazım hatası yok.
```

## Level 1 — Natural

```text
Cümle varyasyonu
Daha günlük kelimeler
Çok düşük hata oranı
```

## Level 2 — Human

```text
Yüklem varyasyonları
Az miktarda ayrı/bitişik hata
Hafif noktalama düzensizliği
```

## Level 3 — Casual

```text
Konuşma dili
geliyorum → geliyom
geleceğim → gelicem
bir şey → birşey
```

## Level 4 — Sloppy

```text
Typo
noktalama eksikleri
fonetik yazım
bazı Türkçe karakter kayıpları
```

Bu seviyenin profesyonel kullanımda sınırlı kullanılması gerekir.

---

# 22. Error Budget

Her çıktı için bir maksimum hata bütçesi belirlenebilir.

Örnek:

```yaml
max_errors_per_100_words: 5
max_errors_per_sentence: 1
max_predicate_errors_per_paragraph: 2
max_typo_errors_per_paragraph: 1
```

Bu yapı metnin aşırı bozulmasını engeller.

---

# 23. Aynı Hatanın Tekrarını Önleme

İnsanlar hata yapar ancak aynı kısa paragrafta sürekli aynı yapıyı bozmak yapay görünür.

Örneğin şu kötü bir çıktı olur:

```text
geliyom
gidiyom
bakıyom
yapıyom
istiyom
```

Tek paragrafta bütün `-yorum` yapılarını bozmak model davranışı gibi görünür.

Bu nedenle cooldown sistemi kullanılabilir.

```yaml
error_cooldown:
  spoken_yor:
    sentences: 3
```

---

# 24. Cümle Seviyesi Doğallık

Humanization yalnızca kelime bazlı olmamalıdır.

Aşağıdaki özellikler de çeşitlendirilmelidir:

- Cümle uzunluğu,
- Bağlaç kullanımı,
- Paragraf uzunluğu,
- Zamir kullanımı,
- Tekrar,
- Eksiltili cümle,
- Resmiyet derecesi.

LLM:

```text
Kontroller gerçekleştirilmiş olup herhangi bir problem tespit edilmemiştir.
Sistemin mevcut durumda normal şekilde çalıştığı görülmektedir.
```

Naturalized:

```text
Kontrolleri yaptım, şu an bir problem görünmüyor.
Sistem normal şekilde çalışıyor.
```

---

# 25. Ana Mimari

```text
                     ┌────────────────────┐
                     │    User / API      │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │ Original LLM Text  │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │ Turkish Naturalizer│
                     └─────────┬──────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │ Morphological Analyzer │
                   └───────────┬────────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │ Candidate Scoring  │
                     └─────────┬──────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │   Human Error Engine   │
                   ├────────────────────────┤
                   │ Predicate Errors       │
                   │ Lexical Errors         │
                   │ de/da ki mi            │
                   │ Phonetic Variations    │
                   │ Typo Engine            │
                   │ Punctuation Engine     │
                   └───────────┬────────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │ Semantic Guardian  │
                     └─────────┬──────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │ Quality Gate │
                       └───────┬──────┘
                               │
                         PASS  │  FAIL
                         ┌─────┘   └─────┐
                         ▼               ▼
                   Final Output       Retry
```

---

# 26. MVP İçin Model Eğitmek Gerekli mi?

İlk sürüm için hayır.

İlk MVP:

```text
Existing LLM
+
Prompt-based Naturalizer
+
Rule-based Human Error Engine
+
Morphological Analysis
+
Semantic Guardian
```

şeklinde oluşturulabilir.

Bu yaklaşım:

- Daha hızlı geliştirilir,
- Daha kolay debug edilir,
- Hataların neden oluştuğu görülebilir,
- Parametreler kontrol edilebilir,
- Dataset oluşmadan başlanabilir.

---

# 27. MVP Teknoloji Yaklaşımı

Önerilen örnek teknoloji seti:

```text
Language:
Python

API:
FastAPI

NLP:
Turkish tokenizer
Morphological analyzer
POS tagging
Dependency parsing

LLM:
API-based LLM veya local model

Semantic Similarity:
Multilingual / Turkish sentence embeddings

Storage:
PostgreSQL veya SQLite

Config:
YAML

Testing:
pytest
```

---

# 28. Önerilen Proje Yapısı

```text
turkish-humanizer/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── humanize.py
│   │
│   ├── naturalizer/
│   │   ├── naturalizer.py
│   │   └── prompts.py
│   │
│   ├── morphology/
│   │   ├── analyzer.py
│   │   ├── tokenizer.py
│   │   └── dependency.py
│   │
│   ├── error_engine/
│   │   ├── engine.py
│   │   ├── scoring.py
│   │   ├── predicate_rules.py
│   │   ├── lexical_rules.py
│   │   ├── phonetic_rules.py
│   │   ├── typo_rules.py
│   │   ├── punctuation_rules.py
│   │   └── spacing_rules.py
│   │
│   ├── guardian/
│   │   ├── semantic.py
│   │   ├── negation.py
│   │   ├── protected_tokens.py
│   │   └── quality_gate.py
│   │
│   ├── personas/
│   │   ├── technical_engineer.yaml
│   │   ├── casual.yaml
│   │   └── whatsapp.yaml
│   │
│   └── config/
│       └── settings.yaml
│
├── data/
│   ├── human_error_dictionary.json
│   ├── predicate_patterns.json
│   └── known_mistakes.json
│
├── tests/
│   ├── test_predicates.py
│   ├── test_semantics.py
│   ├── test_negation.py
│   └── test_protected_tokens.py
│
├── scripts/
│   ├── build_dataset.py
│   └── evaluate.py
│
├── requirements.txt
├── README.md
└── docker-compose.yml
```

---

# 29. API Tasarımı

Örnek endpoint:

```http
POST /humanize
```

Request:

```json
{
  "text": "Kontroller gerçekleştirilmiştir ve herhangi bir problem tespit edilmemiştir.",
  "style": "technical_engineer",
  "humanization": 0.7,
  "error_level": 2
}
```

Response:

```json
{
  "original": "Kontroller gerçekleştirilmiştir ve herhangi bir problem tespit edilmemiştir.",
  "output": "Kontrolleri yaptım, şu an bir problem görünmüyor.",
  "changes": [
    {
      "type": "naturalization",
      "from": "Kontroller gerçekleştirilmiştir",
      "to": "Kontrolleri yaptım"
    }
  ],
  "semantic_score": 0.96,
  "quality_passed": true
}
```

---

# 30. Debug Modu

Geliştirme aşamasında sistem yaptığı her değişikliği açıklayabilmelidir.

```json
{
  "token": "geleceğim",
  "rule": "future_1sg_spoken",
  "before": "geleceğim",
  "after": "gelicem",
  "probability": 0.18,
  "triggered": true
}
```

Bu yapı hata motorunun ayarlanmasını çok kolaylaştıracaktır.

---

# 31. Veri Seti Oluşturma

İlerleyen aşamada gerçek model eğitimi için paired dataset oluşturulabilir.

Format:

```text
CLEAN:
Toplantının yarın saat 14.00'te gerçekleştirilmesi planlanmaktadır.

HUMAN:
Toplantıyı yarın 14.00 gibi yapmayı planlıyoruz.
```

Başka örnek:

```text
CLEAN:
Sistemde herhangi bir problem tespit edilmemiştir.

HUMAN:
Sistemde şu an için bir problem görmedik.
```

Daha gündelik:

```text
CLEAN:
Yarın tekrar kontrol edeceğim.

HUMAN:
Yarın bi daha bakıcam.
```

---

# 32. Dataset Metadata

Her örnek yalnızca clean/human çifti içermemelidir.

Önerilen şema:

```json
{
  "clean": "Yarın tekrar kontrol edeceğim.",
  "human": "Yarın bi daha bakıcam.",
  "style": "casual",
  "errors": [
    "lexical_reduction",
    "future_predicate_spoken"
  ],
  "formality": 0.25,
  "semantic_change": false
}
```

---

# 33. Dataset Kaynakları

Uzun vadede veri aşağıdaki kaynaklardan oluşturulabilir:

- İnsanların gerçek chat mesajları,
- Forumlar,
- Sosyal medya,
- Müşteri destek konuşmaları,
- İnsan tarafından yazılmış e-postalar,
- Teknik ekip mesajları,
- Elle anotasyon,
- Synthetic + human reviewed örnekler.

Kişisel veri ve izin konusu ayrıca ele alınmalıdır.

---

# 34. Fine-Tuning Aşaması

Yeterli veri oluştuğunda Naturalizer modeli fine-tune edilebilir.

Hedef:

```text
Formal / LLM Turkish
        ↓
Human Turkish
```

Modelin görevi typo üretmek olmak zorunda değildir.

Daha doğru ayrım:

```text
Fine-tuned model:
    style transformation

Rule engine:
    controlled errors
```

Böylece davranış daha kontrol edilebilir olur.

---

# 35. Gelecekte Öğrenilecek Olasılık

İlk sürüm:

```text
Manual weights
```

Sonraki sürüm:

```text
P(error | word, suffix, POS, position, persona, platform)
```

Örnek:

```text
P(geliyorum → geliyom | whatsapp) = high

P(geliyorum → geliyom | formal_business) = very low

P(bir şey → birşey | casual) = medium

P(bir şey → birşey | technical_report) = low
```

Bu olasılıklar gerçek corpus üzerinden öğrenilebilir.

---

# 36. Platform Farkındalığı

İnsan yazım davranışı platforma göre değişebilir.

Örnek platformlar:

```text
email
whatsapp
slack
discord
forum
social_media
technical_report
customer_support
```

`WhatsApp` profili ile `technical_report` profilinin aynı hata dağılımına sahip olması beklenmemelidir.

---

# 37. Kullanıcıya Özel Stil Profili

İleri sürümde sistem belirli bir kullanıcının yazım özelliklerini öğrenebilir.

Örneğin:

```text
User frequently:
- skips commas
- writes "birşey"
- uses short sentences
- uses "şuan"
- writes "yapıcaz"
- rarely uses emojis
```

Böylece:

```text
generic_human
```

yerine:

```text
user_style_embedding
```

kullanılabilir.

Bu özellik açık izinle ve gizlilik prensipleriyle tasarlanmalıdır.

---

# 38. A/B Değerlendirme

Sistemin başarısı yalnızca dilbilgisi ile ölçülmemelidir.

Asıl soru:

> İnsan okuyucu bu metni doğal buluyor mu?

Önerilen test:

```text
Original LLM
vs
Humanized Version
vs
Real Human Text
```

Değerlendiricilere:

```text
Hangisi daha doğal?
Hangisi AI tarafından yazılmış gibi?
Hangisi günlük Türkçeye daha yakın?
Anlam değişmiş mi?
```

soruları yöneltilebilir.

---

# 39. Temel Metrikler

Önerilen metrikler:

```text
Semantic Preservation Score

Human Preference Rate

AI Detection Rate
(secondary / experimental)

Error Naturalness Score

Readability Score

Meaning Change Rate

Protected Token Violation Rate

Negation Violation Rate
```

En kritik metrikler:

```text
Meaning Change Rate ≈ 0

Protected Token Violation Rate = 0

Negation Violation Rate = 0
```

olmalıdır.

---

# 40. Test Senaryoları

## Sayı Koruma

Input:

```text
Toplam 120 cihazdan 17 tanesinde sorun görüldü.
```

Çıktıdaki sayılar:

```text
120
17
```

aynı kalmalıdır.

---

## Negation

Input:

```text
Bu cihaz güncellenmemelidir.
```

Kabul:

```text
Bu cihazı güncellememek gerekiyor.
```

Red:

```text
Bu cihaz güncellenmeli.
```

---

## Device ID

Input:

```text
4B3338E8 cihazında hata bulunamadı.
```

ID hiçbir zaman değişmemelidir.

---

## Predicate Humanization

Input:

```text
Yarın tekrar kontrol edeceğim.
```

Casual:

```text
Yarın bi daha bakıcam.
```

Formal business:

```text
Yarın tekrar kontrol edeceğim.
```

---

# 41. MVP Fazları

## Faz 1 — Rule Engine

Amaç:

```text
Human Error Engine v0.1
```

İçerik:

- 100–200 sık Türkçe hata pattern'i,
- Yüklem dönüşümleri,
- `de/da`,
- `ki`,
- `mi`,
- Typo engine,
- Protected tokens.

---

## Faz 2 — Naturalizer

- LLM style transformation,
- Formal → natural,
- Sentence variation,
- Persona desteği.

---

## Faz 3 — Semantic Guardian

- Embedding similarity,
- Numbers,
- IDs,
- Negation,
- Named entities,
- Quality gate.

---

## Faz 4 — Dataset

Hedef:

```text
5.000+ clean/human pair
```

Başlangıç için:

```text
1.000 yüksek kaliteli örnek
```

bile faydalı olabilir.

---

## Faz 5 — Fine-Tuning

Dataset yeterli hale geldiğinde:

```text
Turkish Naturalizer Model
```

fine-tune edilir.

Human Error Engine yine ayrı tutulur.

---

## Faz 6 — Learned Error Distribution

Gerçek insan verilerinden:

```text
P(error | context)
```

öğrenilir.

Elle verilen ağırlıklar zamanla veri tabanlı hale gelir.

---

# 42. İlk Human Error Dictionary Hedefi

İlk dataset:

```text
200 pattern
```

şeklinde başlayabilir.

Kategoriler:

```text
50 predicate / suffix
50 known misspelling
30 de/da/ki/mi
20 compound-spacing
20 phonetic
20 typo
10 punctuation
```

Daha sonra:

```text
500
1.000
5.000+
```

pattern'e çıkılabilir.

---

# 43. Örnek Final Dönüşüm

LLM:

```text
Yapılan kontroller sonucunda cihaz tarafında herhangi bir anomaliye
rastlanmamıştır. Bununla birlikte, sistem loglarının belirli bir süre daha
izlenmesi önerilmektedir.
```

### technical_engineer

```text
Kontrolleri yaptım, şu an cihaz tarafında bir problem görünmüyor.
Yine de logları bir süre daha takip etmekte fayda var.
```

### casual_business

```text
Kontrolleri yaptım, şuan cihaz tarafında bir problem görünmüyor.
Yine de logları biraz daha takip edelim.
```

### whatsapp

```text
Kontrol ettim şuan cihaz tarafında bi problem görünmüyor.
Yine de loglara biraz daha bakalım.
```

### slightly_sloppy

```text
Kontrol ettim şuan cihaz tarafında bi problem görünmüyor
yinede loglara biraz daha bakalım
```

Aynı anlam farklı insan yazım profilleriyle üretilebilir.

---

# 44. En Önemli Tasarım Kararları

## 1. Hata üretmek LLM'e tamamen bırakılmamalı

Çünkü:

- Kontrol edilemez,
- Fazla hata yapabilir,
- Anlam değiştirebilir,
- Aynı hata tipini tekrar tekrar kullanabilir.

---

## 2. Human Error Engine deterministic + probabilistic hibrit olmalı

Kurallar belli olmalı.

Uygulanıp uygulanmayacağı olasılıksal olmalı.

---

## 3. Türkçe morfoloji bilinmeli

Özellikle:

```text
fiiller
ekler
olumsuzluk
de/da
ki
mi
```

kritiktir.

---

## 4. Anlam koruma sistemi zorunlu

Humanizer hiçbir zaman:

```text
meaning corruption engine
```

haline dönüşmemelidir.

---

## 5. Typo ana özellik değil

Typo yalnızca küçük bir alt bileşendir.

Asıl değer:

```text
Natural Style
+
Morphological Humanization
+
Real Error Distribution
+
Semantic Preservation
```

kombinasyonundadır.

---

# 45. Ürünün Potansiyel Konumlandırması

Bu sistem:

```text
"AI text humanizer"
```

şeklinde tanımlanabilir ancak teknik olarak daha güçlü bir tanım:

> **Controllable Turkish Human Writing Model**

veya:

> **Turkish Natural Writing Transformation Engine**

olabilir.

Ürünün farkı:

- Türkçeye özel olması,
- Morfoloji bilmesi,
- Rastgele typo üretmemesi,
- İnsan hata dağılımını modellemesi,
- Persona desteklemesi,
- Anlam koruması,
- Teknik tokenları koruması.

---

# 46. Başlangıç İçin Önerilen Çalışma Sırası

```text
1. 200 adet Human Error Dictionary oluştur
2. Predicate transformation engine geliştir
3. Protected token sistemi ekle
4. de/da/ki/mi kurallarını ekle
5. Error scoring sistemi geliştir
6. Persona config sistemi oluştur
7. Naturalizer LLM katmanını ekle
8. Semantic Guardian geliştir
9. FastAPI endpoint oluştur
10. 500–1000 test cümlesi üret
11. İnsan değerlendirmesi yap
12. Hata ağırlıklarını optimize et
13. Dataset toplamaya başla
14. Fine-tuning değerlendir
```

---

# 47. MVP Başarı Kriteri

İlk başarılı MVP için:

```text
✓ Anlam korunuyor
✓ Sayılar değişmiyor
✓ ID / URL / teknik değerler korunuyor
✓ Türkçe doğal görünüyor
✓ Hatalar rastgele değil
✓ Yüklem hataları gerçekçi
✓ Her cümle hatalı değil
✓ Persona değiştirilince çıktı karakteri değişiyor
✓ Sistem debug edilebiliyor
```

---

# 48. Uzun Vadeli Vizyon

Nihai sistem:

```text
Input Text
+
Target Persona
+
Platform
+
Humanization Level
+
Error Level
+
User Style
```

alacak.

Örneğin:

```json
{
  "text": "...",
  "persona": "technical_engineer",
  "platform": "email",
  "humanization": 0.75,
  "error_level": 1,
  "preserve_semantics": true
}
```

ve bağlama uygun Türkçe insan yazımı üretecektir.

Uzun vadede sistem yalnızca hata ekleyen bir araç değil:

> **Türkçe metnin yazım karakterini kontrol eden bir dil katmanı**

haline gelebilir.

---

# 49. Kısa Sonuç

Bu projenin temel yaklaşımı:

```text
LLM
↓
Naturalizer
↓
Turkish Morphology
↓
Weighted Human Error Engine
↓
Semantic Guardian
↓
Human-like Turkish
```

olmalıdır.

En önemli farklılaştırıcı:

> Rastgele typo yerine gerçek Türkçe kullanıcı hatalarını, özellikle yüklem ve ek yapılarını bağlama göre modellemek.

Bu nedenle ilk geliştirilmesi gereken çekirdek bileşen:

```text
Human Error Dictionary
+
Predicate Error Engine
+
Morphological Analyzer
+
Semantic Guardian
```

kombinasyonudur.

---

# 50. Somut NLP Araç Seçimi (Morphological Analyzer Stack)

Bölüm 10, 20 ve 27'de "Morphological Analyzer / POS Tagger / Dependency Parser" defalarca geçiyor ancak hangi kütüphane kullanılacağı belirtilmemişti. Bu, projenin en riskli teknik kararıdır çünkü Human Error Engine ve Semantic Guardian'ın doğruluğu doğrudan buna bağlıdır.

## Değerlendirilen seçenekler

```text
Zemberek-NLP (Java)
  + En olgun Türkçe morfoloji motoru
  + Ek ayrıştırma (suffix decomposition) çok güçlü
  + Yerleşik "de/da" bağlaç vs. ek disambiguation modülü var
    (TurkishMorphologicalDisambiguator)
  - Java, Python'dan JPype/py4j köprüsü gerekir
  - Dependency parsing yok

Zeyrek (Python)
  + Zemberek morfolojisinin Python portu, doğrudan Python entegrasyonu
  - Daha az bakım görüyor, disambiguator eksik/zayıf
  - Dependency parsing yok

Stanza (Stanford NLP)
  + Turkish UD (IMST treebank) ile eğitilmiş tokenize/POS/lemma/dependency
  + Saf Python, kolay entegrasyon
  - Ek düzeyinde morfolojik ayrıştırma Zemberek kadar detaylı değil

Trankit
  + Stanza'ya benzer, transformer tabanlı (XLM-R), UD Turkish desteği
  - Aynı morfoloji sınırlaması, GPU'da daha iyi çalışır

TRmorph
  - Klasik finite-state analiz, aktif bakımı yok, önerilmiyor
```

## Karar: Hibrit stack

```text
Zemberek (JPype üzerinden)
    → suffix-level ayrıştırma (-yorum, -acağım, de/da/ki/mi disambiguation)
    → Human Error Engine'in Bölüm 6 ve 9'daki dönüşümleri için birincil kaynak

Stanza veya Trankit
    → POS tagging + dependency parsing
    → Predicate/yüklem tespiti (Bölüm 5) ve negation guard (Bölüm 18) için
```

**Gerekçe:** Zemberek'in ek grafiği (suffix graph), sistemin temelini oluşturan ek-seviyesi dönüşümler (Bölüm 6) ve de/da/ki/mi ayrımı (Bölüm 9) için en eksiksiz kaynak. Zemberek'in kendi disambiguator'ı ("ben de" bağlaç mı, "evde" ek mi) MVP'de sıfırdan bir sınıflandırıcı yazmak yerine doğrudan kullanılmalı; güven skoru düşük olan durumlar için (Bölüm 51'deki) rule-based fallback devreye girer. Stanza/Trankit ise dependency parse üzerinden cümledeki yüklemi ve olumsuzluk yapısını (Bölüm 18) güvenilir şekilde bulmak için gerekli — Zemberek bunu sağlamıyor.

JVM köprüsü (JPype) production'da ekstra süreç yönetimi gerektirir; bu maliyet, Faz 1 planlamasına (Bölüm 41) eklenmelidir.

---

# 51. Hata Toleransı ve Fallback Stratejisi

Mevcut plan Quality Gate'in (Bölüm 20) başarısız olursa "retry with lower error intensity" dediğini söylüyor ama analiz aşamasının kendisi başarısız olursa (OOV kelime, karışık dil, bozuk cümle) ne olacağı tanımlı değildi.

## Analiz güven eşiği

```text
morphological_confidence(token) < threshold
    → token dönüştürülmez, olduğu gibi bırakılır
```

Tahmin yürütmek yerine dokunmamak tercih edilir — bu, Bölüm 17-18'deki Semantic Guardian ilkesiyle tutarlıdır.

## Code-switching (Türkçe-İngilizce karışık teknik metin)

Protected Tokens listesi (Bölüm 16) yalnızca regex kalıplarına dayanıyordu. Buna otomatik dil tespiti eklenmelidir:

```text
Her token
    ↓
Language ID (örn. fastText lid.176)
    ↓
Token İngilizce/yabancı mı?
    ↓
Evet → otomatik protected token
```

Bu, örneğin "container restart edilmeli" gibi cümlelerde "container" kelimesinin yanlışlıkla bozulmasını engeller.

## Parser / cümle seviyesi başarısızlık

```text
Dependency parse başarısız
  veya
Cümle çok kısa / bozuk yapıda
    ↓
Naturalizer o cümleyi değiştirmeden geçirir
```

## Gecikme (latency) koruması

```text
per_sentence_analysis_timeout: 200ms

Aşılırsa:
    Human Error Engine atlanır
    Yalnızca Naturalizer (stil) veya orijinal metin döner
```

## Genişletilmiş fallback merdiveni (Bölüm 20'yi tamamlar)

```text
1. Tam humanizasyon (rule engine + LLM naturalizer)
2. Azaltılmış humanizasyon (yalnızca rule engine, düşük yoğunluk)
3. Yalnızca stil (naturalization var, hata enjeksiyonu yok)
4. Orijinal metin (son çare, "humanization_failed" olarak loglanır)
```

Her seviye düşüşü, Bölüm 53'teki debug/log şemasına bir `fallback_level` alanı olarak yazılmalıdır.

---

# 52. Zaman / Kaynak Tahmini

Bölüm 41'deki fazlara kaba süre ve kaynak tahmini:

```text
Faz 1 — Rule Engine
  Süre: 3-4 hafta
  Kaynak: 1 backend geliştirici + Türkçe dilbilgisi/morfoloji danışmanlığı
  Not: Zemberek/JPype entegrasyonu bu fazın en riskli kalemi

Faz 2 — Naturalizer (LLM tabanlı stil dönüşümü)
  Süre: 1-2 hafta (prompt mühendisliği + entegrasyon)
  Maliyet: değişken, istek başı ~500-1000 token; hacim arttıkça
  önbellekleme (aynı girdi+persona+seed → aynı çıktı, bkz. Bölüm 53)
  maliyeti düşürür

Faz 3 — Semantic Guardian
  Süre: 2 hafta
  Kaynak: çok dilli / Türkçe embedding modeli entegrasyonu
  (örn. multilingual-e5, LaBSE)

Faz 4 — Dataset (ilk 1.000 örnek)
  Süre: 2-3 hafta, sürekli devam eder
  Kaynak: anotasyon için insan gözden geçirme kapasitesi

Faz 5 — Fine-Tuning
  Süre: dataset yeterli olduğunda ayrı bir proje olarak planlanır
  Kaynak: GPU eğitim maliyeti, ayrı bütçe kalemi

Faz 6 — Learned Error Distribution
  Süre: uzun vadeli, sürekli iterasyon
```

**MVP'ye kadar (Faz 1-3) kaba toplam:** ~7-9 hafta, küçük ekiple (1-2 kişi).

**Maliyet notu:** Ana değişken maliyet Faz 2'deki LLM çağrılarıdır. Hacim arttıkça, stil dönüşümünü küçük/yerel bir modele taşımak (Bölüm 34'teki fine-tuning hedefiyle uyumlu) maliyeti kontrol altına almanın yoludur.

---

# 53. Determinism, Reproducibility ve Versioning

## Seed tabanlı tekrarlanabilirlik

API isteğine opsiyonel bir `seed` alanı eklenmeli:

```json
{
  "text": "...",
  "style": "technical_engineer",
  "seed": 42
}
```

Aynı `text + style + seed` her zaman aynı çıktıyı üretmelidir. Bu, testler ve "farklı bir varyant üret" kullanıcı akışı için gereklidir. Seed verilmezse rastgele üretilir ve response içinde geri döndürülür (kullanıcı sonradan aynı sonucu tekrar isteyebilsin diye).

## Dictionary ve kural versiyonlama

Human Error Dictionary (Bölüm 7-8) ve persona config'leri (Bölüm 15) semver ile versiyonlanmalı:

```json
{
  "dictionary_version": "1.3.0",
  "rule_engine_version": "0.4.1"
}
```

Bölüm 30'daki debug çıktısı bu alanları içerecek şekilde genişletilmeli:

```json
{
  "token": "geleceğim",
  "rule": "future_1sg_spoken",
  "before": "geleceğim",
  "after": "gelicem",
  "probability": 0.18,
  "triggered": true,
  "dictionary_version": "1.3.0",
  "rule_engine_version": "0.4.1",
  "seed": 42,
  "fallback_level": 0
}
```

Böylece dictionary zamanla değişse bile geçmiş bir çıktının hangi kural setiyle üretildiği yeniden kurulabilir.

## Observability

Her istek için yapılandırılmış (structured) loglama önerilir:

```text
latency_naturalizer_ms
latency_morph_analysis_ms
latency_error_engine_ms
latency_guardian_ms
semantic_score
quality_gate_passed
fallback_level
dictionary_version
rule_engine_version
```

MVP için basit yapılandırılmış log yeterlidir; hacim arttıkça p50/p95 latency, quality_gate geçme oranı ve fallback oranı için bir dashboard (Prometheus/Grafana ya da eşdeğeri) eklenmelidir.
