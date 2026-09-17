"""Error Susceptibility Score (Bölüm 11).

Faz 1'de POS/pozisyon ağırlıkları henüz tam morfolojik analizden
gelmediği için basitleştirilmiş bir çarpım kullanılır:

    score = base_weight * persona_rate

`base_weight`, data/predicate_patterns.json içindeki base_weights
tablosundan (Bölüm 5); `persona_rate`, persona YAML'ındaki ilgili
error rate alanından gelir.
"""


def error_score(base_weight: float, persona_rate: float) -> float:
    score = base_weight * persona_rate
    # 0..1 aralığına sıkıştır: olasılık olarak kullanılacak.
    return max(0.0, min(1.0, score))
