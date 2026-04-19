"""Tests for application/services.py."""

import pytest

from tarot_engine.application.dto import EvaluationRequest, EvaluationResponse
from tarot_engine.application.services import VALID_POLICIES, _resolve_policy, evaluate_hand
from tarot_engine.decision.policies import BalancedPolicy, ConservativePolicy, ExpectedValuePolicy
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract


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
