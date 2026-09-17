from app.guardian.negation import negation_preserved


def test_negation_preserved_when_kept():
    original = "Bu cihaz güncellenmemelidir."
    humanized = "Bu cihazı güncellememek gerekiyor."
    assert negation_preserved(original, humanized)


def test_negation_violation_when_dropped():
    original = "Bu cihaz güncellenmemelidir."
    humanized = "Bu cihaz güncellenmeli."
    assert not negation_preserved(original, humanized)
