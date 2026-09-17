"""POST /humanize (Bölüm 29)."""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.error_engine.engine import humanize as run_humanize

router = APIRouter()


class HumanizeRequest(BaseModel):
    text: str
    style: str = "technical_engineer"
    error_level: int = Field(default=2, ge=0, le=4)
    seed: Optional[int] = None


class ChangeItem(BaseModel):
    rule: str
    before: str
    after: str
    probability: float
    triggered: bool


class HumanizeResponse(BaseModel):
    original: str
    output: str
    style: str
    changes: List[ChangeItem]
    quality_passed: bool
    quality_reasons: List[str]
    semantic_score: Optional[float]
    seed: Optional[int]


@router.post("/humanize", response_model=HumanizeResponse)
def humanize_endpoint(request: HumanizeRequest) -> Dict[str, Any]:
    result = run_humanize(
        text=request.text,
        style=request.style,
        seed=request.seed,
        error_level=request.error_level,
    )
    return {
        "original": result.original,
        "output": result.output,
        "style": result.style,
        "changes": [
            {
                "rule": c.rule, "before": c.before, "after": c.after,
                "probability": c.probability, "triggered": c.triggered,
            }
            for c in result.changes if c.triggered
        ],
        "quality_passed": result.quality_gate.passed if result.quality_gate else True,
        "quality_reasons": result.quality_gate.reasons if result.quality_gate else [],
        "semantic_score": result.quality_gate.semantic_score if result.quality_gate else None,
        "seed": result.seed,
    }
