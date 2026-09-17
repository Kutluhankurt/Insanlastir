import sys
import types

import app.morphology.dependency as dependency_module


def _reset_pipeline_cache():
    dependency_module._pipeline = None


class _FakeWord:
    def __init__(self, text, lemma, upos, head, deprel):
        self.text = text
        self.lemma = lemma
        self.upos = upos
        self.head = head
        self.deprel = deprel


class _FakeSentence:
    def __init__(self, words):
        self.words = words


class _FakeDoc:
    def __init__(self, sentences):
        self.sentences = sentences


class _FakePipeline:
    def __call__(self, text):
        return _FakeDoc([_FakeSentence([
            _FakeWord("Yarın", "yarın", "NOUN", 3, "obl"),
            _FakeWord("kontrol", "kontrol", "NOUN", 3, "obj"),
            _FakeWord("edeceğim", "etmek", "VERB", 0, "root"),
        ])])


def _install_fake_stanza(monkeypatch):
    fake_module = types.SimpleNamespace(
        Pipeline=lambda lang, processors, verbose: _FakePipeline(),
        download=lambda lang, verbose: None,
    )
    monkeypatch.setitem(sys.modules, "stanza", fake_module)


def test_find_root_words_empty_when_not_installed(monkeypatch):
    _reset_pipeline_cache()
    monkeypatch.setitem(sys.modules, "stanza", None)
    assert dependency_module.find_root_words("Yarın kontrol edeceğim.") == []


def test_find_root_words_returns_root(monkeypatch):
    _reset_pipeline_cache()
    _install_fake_stanza(monkeypatch)

    roots = dependency_module.find_root_words("Yarın kontrol edeceğim.")
    assert roots == ["edeceğim"]


def test_parse_returns_words_with_deprel(monkeypatch):
    _reset_pipeline_cache()
    _install_fake_stanza(monkeypatch)

    sentences = dependency_module.parse("Yarın kontrol edeceğim.")
    assert len(sentences) == 1
    words = sentences[0]
    assert [w.text for w in words] == ["Yarın", "kontrol", "edeceğim"]
    assert words[2].deprel == "root"


def test_parse_returns_empty_on_pipeline_failure(monkeypatch):
    _reset_pipeline_cache()

    def _boom(lang, processors, verbose):
        raise RuntimeError("model indirilemedi")

    fake_module = types.SimpleNamespace(Pipeline=_boom, download=lambda lang, verbose: None)
    monkeypatch.setitem(sys.modules, "stanza", fake_module)

    assert dependency_module.parse("Yarın kontrol edeceğim.") == []
