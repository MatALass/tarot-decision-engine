"""Tests for application/services.py."""

import pytest

from tarot_engine.application.dto import (
    EvaluationRequest,
    EvaluationResponse,
    MoveEvaluationRequest,
    MoveEvaluationResponse,
)
from tarot_engine.application.services import (
    VALID_MOVE_POLICIES,
    VALID_POLICIES,
    _resolve_move_policy,
    _resolve_policy,
    evaluate_hand,
    evaluate_move,
)
from tarot_engine.decision.move_policies import ExpectedScoreMovePolicy
from tarot_engine.decision.policies import BalancedPolicy, ConservativePolicy, ExpectedValuePolicy
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.utils.parsing import format_card_token


def _hand_str() -> str:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    fillers = [c for c in deck if not c.is_bout][:12]
    return ",".join(str(c) for c in bouts + fillers)


def _request(**overrides: object) -> EvaluationRequest:
    defaults: dict[str, object] = dict(
        hand_str=_hand_str(), contracts=(), n_simulations=20,
        seed=42, policy="conservative", risk_weight=0.5,
    )
    defaults.update(overrides)
    return EvaluationRequest(**defaults)  # type: ignore[arg-type]


def _build_move_fixture() -> tuple[str, tuple[str, ...], str]:
    deck = generate_deck()
    remaining = (deck[13], deck[14])
    other_cards = iter(deck[15:])
    completed: list[str] = []
    for trick_index in range(13):
        entries = [f"0:{format_card_token(deck[trick_index])}"]
        for player_index in range(1, 5):
            entries.append(f"{player_index}:{format_card_token(next(other_cards))}")
        completed.append("|".join(entries))
    current_trick = f"4:{format_card_token(next(other_cards))}"
    return ",".join(format_card_token(card) for card in remaining), tuple(completed), current_trick


def _move_request(**overrides: object) -> MoveEvaluationRequest:
    remaining_hand_str, completed_trick_strs, current_trick_str = _build_move_fixture()
    defaults: dict[str, object] = dict(
        remaining_hand_str=remaining_hand_str,
        contract=Contract.GARDE,
        player_index=0,
        taker_index=0,
        partner_index=None,
        completed_trick_strs=completed_trick_strs,
        current_trick_str=current_trick_str,
        next_player_index=0,
        n_samples=5,
        seed=7,
        policy="expected_score",
    )
    defaults.update(overrides)
    return MoveEvaluationRequest(**defaults)  # type: ignore[arg-type]


class TestResolvePolicy:
    def test_conservative(self) -> None:
        assert isinstance(_resolve_policy("conservative", 0.5), ConservativePolicy)

    def test_expected_value(self) -> None:
        assert isinstance(_resolve_policy("expected_value", 0.5), ExpectedValuePolicy)

    def test_balanced(self) -> None:
        assert isinstance(_resolve_policy("balanced", 1.5), BalancedPolicy)

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown policy"):
            _resolve_policy("magic", 0.5)

    def test_all_valid_resolve(self) -> None:
        for name in VALID_POLICIES:
            _resolve_policy(name, 0.5)


class TestResolveMovePolicy:
    def test_expected_score(self) -> None:
        assert isinstance(_resolve_move_policy("expected_score"), ExpectedScoreMovePolicy)

    def test_all_valid_resolve(self) -> None:
        for name in VALID_MOVE_POLICIES:
            _resolve_move_policy(name)

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown move policy"):
            _resolve_move_policy("magic")


class TestEvaluationRequestValidation:
    def test_valid(self) -> None:
        assert _request().policy == "conservative"

    def test_invalid_policy_raises(self) -> None:
        with pytest.raises(Exception):
            _request(policy="magic")

    def test_empty_hand_raises(self) -> None:
        with pytest.raises(Exception):
            _request(hand_str="")

    def test_zero_simulations_raises(self) -> None:
        with pytest.raises(Exception):
            _request(n_simulations=0)

    def test_negative_risk_weight_raises(self) -> None:
        with pytest.raises(Exception):
            _request(risk_weight=-0.1)

    def test_immutable(self) -> None:
        with pytest.raises(Exception):
            _request().seed = 999  # type: ignore[misc]


class TestMoveEvaluationRequestValidation:
    def test_valid(self) -> None:
        assert _move_request().policy == "expected_score"

    def test_invalid_move_policy_raises(self) -> None:
        with pytest.raises(Exception):
            _move_request(policy="magic")

    def test_empty_remaining_hand_raises(self) -> None:
        with pytest.raises(Exception):
            _move_request(remaining_hand_str="")


class TestEvaluateHandService:
    def test_returns_response(self) -> None:
        assert isinstance(evaluate_hand(_request()), EvaluationResponse)

    def test_recommended_contract_is_valid(self) -> None:
        assert evaluate_hand(_request()).recommendation.recommended_contract in Contract

    def test_default_evaluates_all_four_contracts(self) -> None:
        response = evaluate_hand(_request(contracts=()))
        assert {ev.contract for ev in response.evaluations} == set(Contract)

    def test_subset_contracts(self) -> None:
        response = evaluate_hand(_request(contracts=(Contract.PRISE, Contract.GARDE)))
        assert {ev.contract for ev in response.evaluations} == {Contract.PRISE, Contract.GARDE}

    def test_reproducible(self) -> None:
        r1 = evaluate_hand(_request(seed=7))
        r2 = evaluate_hand(_request(seed=7))
        assert r1.recommendation.recommended_contract == r2.recommendation.recommended_contract

    def test_all_policies_succeed(self) -> None:
        for policy in VALID_POLICIES:
            evaluate_hand(_request(policy=policy))

    def test_invalid_hand_raises(self) -> None:
        with pytest.raises(ValueError):
            evaluate_hand(_request(hand_str="NOT,VALID,CARDS"))

    def test_wrong_hand_size_raises(self) -> None:
        with pytest.raises(ValueError):
            evaluate_hand(_request(hand_str="T21,KH,EXCUSE"))

    def test_evaluations_in_ranking_order(self) -> None:
        response = evaluate_hand(_request())
        assert [ev.contract for ev in response.evaluations] == [
            rc.evaluation.contract for rc in response.recommendation.ranked_contracts
        ]


class TestEvaluateMoveService:
    def test_returns_response(self) -> None:
        assert isinstance(evaluate_move(_move_request()), MoveEvaluationResponse)

    def test_recommended_action_player_matches_observed(self) -> None:
        response = evaluate_move(_move_request())
        assert response.recommendation.recommended_action.player_index == 0

    def test_reproducible(self) -> None:
        r1 = evaluate_move(_move_request(seed=11, n_samples=3))
        r2 = evaluate_move(_move_request(seed=11, n_samples=3))
        assert r1.recommendation.recommended_action == r2.recommendation.recommended_action

    def test_invalid_trick_size_raises(self) -> None:
        with pytest.raises(ValueError, match="exactly 5"):
            evaluate_move(
                _move_request(completed_trick_strs=("0:T21|1:T20",), current_trick_str="")
            )
