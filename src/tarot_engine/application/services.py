"""Application service: orchestrate evaluation from request to response."""

from __future__ import annotations

from tarot_engine.application.dto import EvaluationRequest, EvaluationResponse
from tarot_engine.decision.evaluator import evaluate_contracts
from tarot_engine.decision.policies import (
    BalancedPolicy,
    ConservativePolicy,
    DecisionPolicy,
    ExpectedValuePolicy,
)
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.simulation.monte_carlo import SimulationConfig
from tarot_engine.utils.parsing import parse_hand_string

VALID_POLICIES: tuple[str, ...] = ("conservative", "expected_value", "balanced")


def evaluate_hand(request: EvaluationRequest) -> EvaluationResponse:
    """Execute a full hand evaluation.

    Raises:
        ValueError: If the hand string or parameters are invalid.
    """
    cards = parse_hand_string(request.hand_str)
    hand = Hand.from_cards(cards)
    contracts: list[Contract] = (
        list(request.contracts) if request.contracts else list(Contract)
    )
    config = SimulationConfig(n_simulations=request.n_simulations, seed=request.seed)
    evaluations = evaluate_contracts(hand, contracts, config)
    policy = _resolve_policy(request.policy, request.risk_weight)
    recommendation = policy.choose(evaluations)
    return EvaluationResponse(
        recommendation=recommendation,
        evaluations=tuple(rc.evaluation for rc in recommendation.ranked_contracts),
    )


def _resolve_policy(name: str, risk_weight: float) -> DecisionPolicy:
    if name == "conservative":
        return ConservativePolicy()
    if name == "expected_value":
        return ExpectedValuePolicy()
    if name == "balanced":
        return BalancedPolicy(risk_weight=risk_weight)
    raise ValueError(
        f"Unknown policy '{name}'. Valid options: {', '.join(VALID_POLICIES)}."
    )
