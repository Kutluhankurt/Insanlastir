"""Semantic Similarity (Bölüm 19).

`sentence-transformers` kuruluysa (`pip install -e ".[semantic]"`) çok
dilli embedding tabanlı cosine similarity hesaplar
(`intfloat/multilingual-e5-small`). Kurulu değilse (varsayılan) None
döner ve Quality Gate bu kontrolü atlar (Bölüm 51 fallback felsefesi).

Bu katman `llm` extra'sından farklıdır: API maliyeti yoktur (model
yerel olarak çalışır), ama ilk çalıştırmada Hugging Face'ten ~470MB'lık
model ağırlığı indirilir ve `torch` gibi ağır bir bağımlılık gerektirir
- bu yüzden opt-in tutuldu, Faz 1/2'nin hafif kurulumunu bozmasın diye.
"""
import sys
from typing import Optional

_MODEL_NAME = "intfloat/multilingual-e5-small"
_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    from sentence_transformers import SentenceTransformer

    _model = SentenceTransformer(_MODEL_NAME)
    return _model


def cosine_similarity(original: str, humanized: str) -> Optional[float]:
    try:
        model = _load_model()
        from sentence_transformers import util
    except ImportError:
        return None
    except Exception as exc:
        print(f"[semantic] embedding modeli yüklenemedi: {exc}", file=sys.stderr)
        return None

    try:
        # e5 model ailesi giriş metinlerinin "query: " öneki ile
        # kodlanmasını bekler (bkz. model kartı).
        embeddings = model.encode(
            [f"query: {original}", f"query: {humanized}"],
            normalize_embeddings=True,
        )
        return float(util.cos_sim(embeddings[0], embeddings[1]).item())
    except Exception as exc:
        print(f"[semantic] benzerlik hesaplanamadı: {exc}", file=sys.stderr)
        return None
