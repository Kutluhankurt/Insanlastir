import sys
import types

import app.guardian.semantic as semantic_module


def _reset_model_cache():
    semantic_module._model = None


def test_cosine_similarity_none_when_not_installed(monkeypatch):
    _reset_model_cache()
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    assert semantic_module.cosine_similarity("Merhaba.", "Selam.") is None


def test_cosine_similarity_returns_score_from_mocked_model(monkeypatch):
    _reset_model_cache()

    class FakeModel:
        def encode(self, texts, normalize_embeddings=True):
            return [f"vec::{t}" for t in texts]

    class FakeScore:
        def item(self):
            return 0.97

    fake_util = types.SimpleNamespace(cos_sim=lambda a, b: FakeScore())
    fake_module = types.SimpleNamespace(
        SentenceTransformer=lambda name: FakeModel(),
        util=fake_util,
    )
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)

    score = semantic_module.cosine_similarity("Yarın geleceğim.", "Yarın gelicem.")
    assert score == 0.97


def test_cosine_similarity_none_on_model_load_failure(monkeypatch):
    _reset_model_cache()

    def _boom(name):
        raise RuntimeError("model indirilemedi")

    fake_module = types.SimpleNamespace(SentenceTransformer=_boom, util=types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)

    assert semantic_module.cosine_similarity("a", "b") is None
