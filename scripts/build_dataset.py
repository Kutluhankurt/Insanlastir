"""Faz 4 (Bölüm 31-33): clean/human çift veri seti oluşturma iskeleti.

Şu an yalnızca şema ve CLI iskeleti var; gerçek veri toplama/anotasyon
akışı Faz 4'te doldurulacak.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.error_engine.engine import humanize  # noqa: E402


def build_pair(clean_text: str, style: str, seed: int) -> dict:
    result = humanize(clean_text, style=style, seed=seed, error_level=3)
    return {
        "clean": clean_text,
        "human": result.output,
        "style": style,
        "seed": seed,
        "semantic_change": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean/human örnek çiftleri üretir (Bölüm 32 şeması).")
    parser.add_argument("input", help="Her satırda bir 'clean' cümle içeren metin dosyası")
    parser.add_argument("--style", default="technical_engineer")
    parser.add_argument("--out", default="data/generated_pairs.jsonl")
    args = parser.parse_args()

    lines = Path(args.input).read_text(encoding="utf-8").splitlines()
    with open(args.out, "w", encoding="utf-8") as f:
        for i, line in enumerate(l.strip() for l in lines):
            if not line:
                continue
            pair = build_pair(line, args.style, seed=i)
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
