"""Application services: orchestrate evaluation from request DTOs to response DTOs."""

from __future__ import annotations

from tarot_engine.application.dto import (
    EvaluationRequest,
    EvaluationResponse,
    MoveEvaluationRequest,
    MoveEvaluationResponse,
)
from tarot_engine.decision.evaluator import evaluate_contracts
from tarot_engine.decision.move_explainer import explain_move
from tarot_engine.decision.move_policies import ExpectedScoreMovePolicy, MoveDecisionPolicy
from tarot_engine.decision.policies import (
    BalancedPolicy,
    ConservativePolicy,
    DecisionPolicy,
    ExpectedValuePolicy,
)
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import Trick, trick_winner
from tarot_engine.domain.trick import CompletedTrick, TrickHistory
from tarot_engine.simulation.action_evaluator import EvaluatorConfig, evaluate_actions
from tarot_engine.simulation.monte_carlo import SimulationConfig
from tarot_engine.utils.parsing import parse_hand_string, parse_trick_string

VALID_POLICIES: tuple[str, ...] = ("conservative", "expected_value", "balanced")
VALID_MOVE_POLICIES: tuple[str, ...] = ("expected_score",)


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



def evaluate_move(request: MoveEvaluationRequest) -> MoveEvaluationResponse:
    """Execute a full turn-by-turn move evaluation from an intermediate state."""
    game_state = _build_game_state_from_request(request)
    config = EvaluatorConfig(n_samples=request.n_samples, seed=request.seed)
    evaluations = evaluate_actions(game_state, config=config)
    policy = _resolve_move_policy(request.policy)
    recommendation = policy.choose(evaluations)
    return MoveEvaluationResponse(
        recommendation=recommendation,
        evaluations=tuple(ranked.evaluation for ranked in recommendation.ranked_actions),
        explanation=explain_move(recommendation),
    )



def _build_game_state_from_request(request: MoveEvaluationRequest) -> GameState:
    remaining_hand = tuple(parse_hand_string(request.remaining_hand_str))
    completed_tricks = tuple(
        _parse_completed_trick(trick_str, trick_number=index + 1)
        for index, trick_str in enumerate(request.completed_trick_strs)
    )
    current_trick = parse_trick_string(request.current_trick_str) if request.current_trick_str.strip() else ()

    own_played_cards = tuple(
        trick_card.card
        for trick in completed_tricks
        for trick_card in trick.cards
        if trick_card.player_index == request.player_index
    ) + tuple(
        trick_card.card
        for trick_card in current_trick
        if trick_card.player_index == request.player_index
    )

    initial_hand = Hand.from_cards(list(remaining_hand + own_played_cards))
    context = InitialDealContext(
        player_index=request.player_index,
        taker_index=request.taker_index,
        contract=request.contract,
        initial_hand=initial_hand,
        partner_index=request.partner_index,
    )
    return GameState(
        context=context,
        remaining_hand=remaining_hand,
        current_trick=current_trick,
        completed_tricks=TrickHistory(tricks=completed_tricks),
        next_player_index=request.next_player_index,
    )



def _parse_completed_trick(trick_str: str, *, trick_number: int) -> CompletedTrick:
    cards = parse_trick_string(trick_str)
    if len(cards) != 5:
        raise ValueError(
            f"Completed trick #{trick_number} must contain exactly 5 played cards, got {len(cards)}."
        )
    trick = Trick(cards)
    return CompletedTrick(
        cards=cards,
        winner_index=trick_winner(trick),
        lead_player_index=cards[0].player_index,
        trick_number=trick_number,
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



def _resolve_move_policy(name: str) -> MoveDecisionPolicy:
    if name == "expected_score":
        return ExpectedScoreMovePolicy()
    raise ValueError(
        f"Unknown move policy '{name}'. Valid options: {', '.join(VALID_MOVE_POLICIES)}."
    )
