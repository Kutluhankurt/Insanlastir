import sys
import types
from unittest.mock import MagicMock

from app.naturalizer.naturalizer import naturalize


def test_naturalize_passthrough_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert naturalize("Merhaba dünya.", "whatsapp") == "Merhaba dünya."


def test_naturalize_empty_text_passthrough(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    assert naturalize("   ", "whatsapp") == "   "


def test_naturalize_falls_back_when_anthropic_not_installed(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.setitem(sys.modules, "anthropic", None)
    assert naturalize("Kontroller tamamlanmıştır.", "whatsapp") == "Kontroller tamamlanmıştır."


def test_naturalize_calls_llm_and_returns_text(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    text_block = types.SimpleNamespace(type="text", text="Kontrolleri yaptım, sorun yok.")
    fake_response = types.SimpleNamespace(content=[text_block])

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    fake_anthropic_module = types.SimpleNamespace(Anthropic=lambda: fake_client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic_module)

    result = naturalize("Kontroller gerçekleştirilmiştir.", "whatsapp")

    assert result == "Kontrolleri yaptım, sorun yok."
    fake_client.messages.create.assert_called_once()
    _, kwargs = fake_client.messages.create.call_args
    assert kwargs["model"] == "claude-opus-5"
    assert "Kontroller gerçekleştirilmiştir." in kwargs["messages"][0]["content"]


def test_naturalize_swallows_llm_errors(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = RuntimeError("boom")
    fake_anthropic_module = types.SimpleNamespace(Anthropic=lambda: fake_client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic_module)

    assert naturalize("Orijinal metin.", "whatsapp") == "Orijinal metin."
