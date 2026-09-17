from app.guardian.protected_tokens import find_protected_spans, is_inside_protected


def test_device_id_protected():
    text = "Device ID 4B3338E8, Engine v1.4.2 ve IP 192.168.1.20"
    spans = find_protected_spans(text)
    values = [s.value for s in spans]
    assert "4B3338E8" in values
    assert "192.168.1.20" in values


def test_version_number_protected():
    text = "Engine v1.4.2 güncellendi"
    spans = find_protected_spans(text)
    assert any(s.value == "v1.4.2" for s in spans)


def test_is_inside_protected():
    text = "Cihaz 4B3338E8 çalışıyor"
    spans = find_protected_spans(text)
    idx = text.index("4B3338E8")
    assert is_inside_protected(idx, spans)
    assert not is_inside_protected(0, spans)


def test_known_tech_english_word_protected():
    text = "container restart edilmeli"
    spans = find_protected_spans(text)
    values = [s.value for s in spans]
    assert "container" in values
