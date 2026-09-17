"""Komut satırı arayüzü.

Kurulumdan sonra (`pip install -e .`):
    insanlastir "Yarın tekrar kontrol edeceğim." --style whatsapp

Kurulum yapmadan:
    python -m app.cli "Yarın tekrar kontrol edeceğim." --style whatsapp
"""
import argparse
import json
import sys
from pathlib import Path

from app.error_engine.engine import humanize

_PERSONAS_DIR = Path(__file__).resolve().parent / "personas"


def _available_styles():
    return sorted(p.stem for p in _PERSONAS_DIR.glob("*.yaml"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="insanlastir",
        description="Türkçe LLM çıktısını daha doğal insan yazımına yaklaştırır (Faz 1 rule engine).",
    )
    parser.add_argument("text", nargs="?", help="Humanize edilecek metin. Verilmezse stdin'den okunur.")
    parser.add_argument("--style", default="technical_engineer", choices=_available_styles())
    parser.add_argument("--error-level", type=int, default=2, choices=[0, 1, 2, 3, 4],
                         help="0=Clean, 1=Natural, 2=Human, 3=Casual, 4=Sloppy (plan Bölüm 21)")
    parser.add_argument("--seed", type=int, default=None, help="Tekrarlanabilir çıktı için rastgelelik tohumu")
    parser.add_argument("--json", action="store_true", help="Debug trace dahil JSON çıktı ver")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    text = args.text
    if text is None:
        text = sys.stdin.read().strip()
    if not text:
        print("Hata: humanize edilecek metin verilmedi.", file=sys.stderr)
        return 1

    result = humanize(text, style=args.style, seed=args.seed, error_level=args.error_level)

    if args.json:
        payload = {
            "original": result.original,
            "output": result.output,
            "style": result.style,
            "seed": result.seed,
            "changes": [
                {"rule": c.rule, "before": c.before, "after": c.after, "probability": c.probability}
                for c in result.changes if c.triggered
            ],
            "quality_passed": result.quality_gate.passed if result.quality_gate else True,
            "quality_reasons": result.quality_gate.reasons if result.quality_gate else [],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(result.output)
        if result.quality_gate and not result.quality_gate.passed:
            print(f"[uyarı] quality gate geçmedi: {result.quality_gate.reasons}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
