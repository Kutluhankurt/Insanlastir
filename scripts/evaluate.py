"""Bölüm 39: temel metrikleri hesaplayan değerlendirme iskeleti.

Faz 1 kapsamında yalnızca Protected Token Violation Rate ve Negation
Violation Rate hesaplanabiliyor (Semantic Guardian embedding'i Faz 3'te
eklenecek, bkz. app/guardian/semantic.py).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.guardian.negation import negation_preserved  # noqa: E402
from app.guardian.quality_gate import evaluate as quality_gate_evaluate  # noqa: E402


def evaluate_pairs(pairs_path: str) -> dict:
    total = 0
    negation_violations = 0
    protected_violations = 0

    with open(pairs_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pair = json.loads(line)
            total += 1
            original, humanized = pair["clean"], pair["human"]

            if not negation_preserved(original, humanized):
                negation_violations += 1

            qg = quality_gate_evaluate(original, humanized, error_count=1, word_count=max(1, len(original.split())))
            if "protected_token_violation" in qg.reasons:
                protected_violations += 1

    return {
        "total": total,
        "negation_violation_rate": negation_violations / total if total else 0.0,
        "protected_token_violation_rate": protected_violations / total if total else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bölüm 39 temel metriklerini hesaplar.")
    parser.add_argument("pairs", help="build_dataset.py çıktısı .jsonl dosyası")
    args = parser.parse_args()
    print(json.dumps(evaluate_pairs(args.pairs), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
