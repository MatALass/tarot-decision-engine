"""Application-layer data transfer objects (Pydantic).

These objects cross the external boundary (CLI / future API → service layer).
Pydantic provides validation and immutability at that boundary.
Internal domain objects remain plain frozen dataclasses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from tarot_engine.decision.models import ContractEvaluation, DecisionRecommendation
from tarot_engine.domain.enums import Contract


class EvaluationRequest(BaseModel):
    """Input to the hand evaluation service."""

    model_config = {"frozen": True}

    hand_str: str
    contracts: tuple[Contract, ...] = Field(default=())
    n_simulations: int = Field(default=1_000, ge=1, le=100_000)
    seed: int = Field(default=0)
    policy: str = Field(default="conservative")
    risk_weight: float = Field(default=0.5, ge=0.0)

    @field_validator("policy")
    @classmethod
    def policy_must_be_valid(cls, v: str) -> str:
        valid = {"conservative", "expected_value", "balanced"}
        if v not in valid:
            raise ValueError(
                f"Unknown policy '{v}'. Valid options: {', '.join(sorted(valid))}."
            )
        return v

    @field_validator("hand_str")
    @classmethod
    def hand_str_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("hand_str must not be empty.")
        return v


class EvaluationResponse(BaseModel):
    """Output of the hand evaluation service."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    recommendation: DecisionRecommendation
    evaluations: tuple[ContractEvaluation, ...]
