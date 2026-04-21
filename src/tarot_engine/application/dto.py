"""Application-layer data transfer objects (Pydantic).

These objects cross the external boundary (CLI / future API → service layer).
Pydantic provides validation and immutability at that boundary.
Internal domain objects remain plain frozen dataclasses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from tarot_engine.decision.models import ContractEvaluation, DecisionRecommendation
from tarot_engine.decision.move_explainer import MoveExplanation
from tarot_engine.domain.enums import Contract
from tarot_engine.simulation.action_evaluator import ActionEvaluation, MoveRecommendation


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


class MoveEvaluationRequest(BaseModel):
    """Input DTO for turn-by-turn move recommendation from an intermediate state."""

    model_config = {"frozen": True}

    remaining_hand_str: str
    contract: Contract
    player_index: int = Field(ge=0, le=4)
    taker_index: int = Field(ge=0, le=4)
    partner_index: int | None = Field(default=None, ge=0, le=4)
    current_trick_str: str = Field(default="")
    completed_trick_strs: tuple[str, ...] = Field(default=())
    next_player_index: int = Field(ge=0, le=4)
    n_samples: int = Field(default=200, ge=1, le=100_000)
    seed: int = Field(default=0)
    policy: str = Field(default="expected_score")
    risk_weight: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("remaining_hand_str")
    @classmethod
    def remaining_hand_str_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("remaining_hand_str must not be empty.")
        return v

    @field_validator("policy")
    @classmethod
    def move_policy_must_be_valid(cls, v: str) -> str:
        valid = {"expected_score", "robust_score", "balanced"}
        if v not in valid:
            raise ValueError(
                f"Unknown move policy '{v}'. Valid options: {', '.join(sorted(valid))}."
            )
        return v

    @field_validator("partner_index")
    @classmethod
    def partner_cannot_equal_taker(cls, v: int | None, info) -> int | None:
        if v is not None and "taker_index" in info.data and v == info.data["taker_index"]:
            raise ValueError("partner_index cannot be equal to taker_index.")
        return v


class MoveEvaluationResponse(BaseModel):
    """Output DTO for turn-by-turn move recommendation."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    recommendation: MoveRecommendation
    evaluations: tuple[ActionEvaluation, ...]
    explanation: MoveExplanation
