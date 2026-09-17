from app.error_engine import engine as engine_module
from app.error_engine import scoring


def test_root_predicate_gets_weight_boost(monkeypatch):
    """dependency.find_root_words ROOT olarak işaretlerse, o kelime
    verb_yor (3.5) yerine predicate (4.0) ağırlığıyla skorlanmalı."""
    monkeypatch.setattr(engine_module.dependency, "find_root_words", lambda text: ["gidiyorum"])

    result = engine_module.humanize(
        "Ben gidiyorum, sen de biliyorsun.", style="technical_engineer", seed=1, error_level=3,
    )

    root_change = next(c for c in result.changes if c.before == "gidiyorum")
    assert root_change.probability == scoring.error_score(4.0, 0.12)


def test_non_root_predicate_keeps_suffix_weight(monkeypatch):
    """dependency bulunamazsa (stanza kurulu değil, varsayılan) eski
    davranış korunmalı: yalnızca ek ağırlığı (verb_yor=3.5) kullanılır."""
    monkeypatch.setattr(engine_module.dependency, "find_root_words", lambda text: [])

    result = engine_module.humanize(
        "Ben gidiyorum, sen de biliyorsun.", style="technical_engineer", seed=1, error_level=3,
    )

    root_change = next(c for c in result.changes if c.before == "gidiyorum")
    assert root_change.probability == scoring.error_score(3.5, 0.12)
