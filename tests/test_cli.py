from app.cli import build_parser, main


def test_parser_defaults():
    args = build_parser().parse_args(["merhaba"])
    assert args.text == "merhaba"
    assert args.style == "technical_engineer"
    assert args.error_level == 2


def test_main_prints_output(capsys):
    exit_code = main(["Yarın tekrar kontrol edeceğim.", "--style", "technical_engineer", "--seed", "1"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() != ""


def test_main_json_output(capsys):
    exit_code = main(["Yarın tekrar kontrol edeceğim.", "--json", "--seed", "1"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"output"' in captured.out


def test_main_requires_text(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin.read", lambda: "")
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Hata" in captured.err
