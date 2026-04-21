"""Public HTTP API schemas.

These schemas intentionally decouple the transport contract from the internal
application DTOs and domain dataclasses. This keeps the HTTP boundary stable
while the engine evolves internally.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ApiHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "tarot-decision-engine"
    api_version: str = "v1"


class ApiContractEvaluationRequest(BaseModel):
    hand: str = Field(..., description="Comma-separated 15-card hand.")
    contracts: list[str] = Field(default_factory=list)
    n_simulations: int = Field(default=1_000, ge=1, le=100_000)
    seed: int = Field(default=0)
    policy: str = Field(default="conservative")
    risk_weight: float = Field(default=0.5, ge=0.0)


class ApiContractEvaluationItem(BaseModel):
    contract: str
    win_rate: float
    expected_score: float
    score_std: float
    score_q10: float
    score_q50: float
    score_q90: float
    n_simulations: int


class ApiContractRecommendationItem(BaseModel):
    rank: int
    contract: str
    expected_score: float
    win_rate: float


class ApiContractEvaluationResponse(BaseModel):
    recommended_contract: str
    policy_name: str
    rationale: str
    warnings: list[str]
    ranked_contracts: list[ApiContractRecommendationItem]
    evaluations: list[ApiContractEvaluationItem]


class ApiMoveEvaluationRequest(BaseModel):
    remaining_hand: str = Field(..., description="Comma-separated remaining hand.")
    contract: str
    player_index: int = Field(ge=0, le=4)
    taker_index: int = Field(ge=0, le=4)
    partner_index: int | None = Field(default=None, ge=0, le=4)
    current_trick: str = Field(default="")
    completed_tricks: list[str] = Field(default_factory=list)
    next_player_index: int = Field(ge=0, le=4)
    n_samples: int = Field(default=200, ge=1, le=100_000)
    seed: int = Field(default=0)
    policy: str = Field(default="expected_score")


class ApiActionReference(BaseModel):
    player_index: int
    card: str


class ApiActionEvaluationItem(BaseModel):
    action: ApiActionReference
    expected_score: float
    win_rate: float
    score_std: float
    score_q10: float
    score_q50: float
    score_q90: float
    n_samples: int


class ApiRankedActionItem(BaseModel):
    rank: int
    action: ApiActionReference
    expected_score: float
    win_rate: float


class ApiMoveExplanation(BaseModel):
    summary: str
    top_gap_expected_score: float
    top_gap_win_rate: float
    risk_comment: str
    alternatives_summary: list[str]


class ApiMoveEvaluationResponse(BaseModel):
    recommended_action: ApiActionReference
    policy_name: str
    rationale: str
    warnings: list[str]
    ranked_actions: list[ApiRankedActionItem]
    evaluations: list[ApiActionEvaluationItem]
    explanation: ApiMoveExplanation
