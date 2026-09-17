from app.error_engine import predicate_rules


def test_yor_1sg():
    r = predicate_rules.transform_yor("geliyorum")
    assert r is not None
    assert r.after == "geliyom"


def test_yor_1pl():
    r = predicate_rules.transform_yor("gidiyoruz")
    assert r is not None
    assert r.after == "gidiyoz"


def test_future_1sg_back_vowel():
    r = predicate_rules.transform_future_1sg("yapacağım")
    assert r is not None
    assert r.after == "yapıcam"


def test_future_1sg_front_vowel():
    r = predicate_rules.transform_future_1sg("geleceğim")
    assert r is not None
    assert r.after == "gelicem"


def test_future_1sg_rounded_back_vowel():
    r = predicate_rules.transform_future_1sg("olacağım")
    assert r is not None
    assert r.after == "olucam"


def test_future_1sg_ed_stem():
    r = predicate_rules.transform_future_1sg("edeceğim")
    assert r is not None
    assert r.after == "edicem"


def test_future_1pl():
    r = predicate_rules.transform_future_1pl("yapacağız")
    assert r is not None
    assert r.after == "yapıcaz"

    r2 = predicate_rules.transform_future_1pl("geleceğiz")
    assert r2 is not None
    assert r2.after == "gelicez"


def test_no_match_returns_none():
    assert predicate_rules.apply_first_matching("masa") is None
