import json
import random
from pathlib import Path

from app.error_engine import baglac_rules

_WEIGHTS = json.load(open(Path(__file__).resolve().parent.parent / "data" / "predicate_patterns.json"))["base_weights"]


def test_de_join():
    out, changes = baglac_rules.apply("ben de geleceğim", _WEIGHTS, rate=1.0, rng=random.Random(1))
    assert out == "bende geleceğim"
    assert changes[0].rule == "de_da_join"


def test_ki_join():
    out, changes = baglac_rules.apply("öyle ki herkes biliyor", _WEIGHTS, rate=1.0, rng=random.Random(1))
    assert out == "öyleki herkes biliyor"
    assert changes[0].rule == "ki_join"


def test_mi_question_particle_join():
    out, changes = baglac_rules.apply("geliyor musun", _WEIGHTS, rate=1.0, rng=random.Random(1))
    assert out == "geliyormusun"
    assert changes[0].rule == "mi_join"


def test_locative_de_not_touched():
    """'evde' -> 'de' zaten ek olarak gövdeye yapışık, ayrı token değil."""
    out, changes = baglac_rules.apply("evde kimse yok", _WEIGHTS, rate=1.0, rng=random.Random(1))
    assert out == "evde kimse yok"
    assert changes == []


def test_protected_token_not_joined():
    out, changes = baglac_rules.apply(
        "Cihaz 4B3338E8 de güncellenmeli.", _WEIGHTS, rate=1.0, rng=random.Random(1),
    )
    assert out == "Cihaz 4B3338E8 de güncellenmeli."
    assert changes == []


def test_zero_rate_never_joins():
    out, changes = baglac_rules.apply("ben de geleceğim", _WEIGHTS, rate=0.0, rng=random.Random(1))
    assert out == "ben de geleceğim"
    assert changes == []
