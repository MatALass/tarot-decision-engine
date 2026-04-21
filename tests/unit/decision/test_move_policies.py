"""Tests for move decision policies."""

from tarot_engine.decision.move_policies import (
    BalancedMovePolicy,
    ExpectedScoreMovePolicy,
    RobustScoreMovePolicy,
)
from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.simulation.action_evaluator import ActionEvaluation


def _evaluation(card: int, *, expected: float, robust: float, win_rate: float) -> ActionEvaluation:
    return ActionEvaluation(
        action=PlayAction(player_index=0, card=Card.trump(card)),
        n_samples=10,
        win_rate=win_rate,
        expected_score=expected,
        robust_score=robust,
        downside_risk=max(0.0, expected - robust),
        score_std=5.0,
        score_min=-20,
        score_max=40,
        score_q05=-10.0,
        score_q10=robust,
        score_q50=expected,
        score_q90=25.0,
        score_q95=30.0,
    )


class TestMovePolicies:
    def test_expected_score_policy_prefers_best_ev(self) -> None:
        evaluations = (
            _evaluation(1, expected=10.0, robust=0.0, win_rate=0.5),
            _evaluation(2, expected=8.0, robust=7.0, win_rate=0.6),
        )

        recommendation = ExpectedScoreMovePolicy().choose(evaluations)

        assert recommendation.recommended_action.card == Card.trump(1)

    def test_robust_score_policy_prefers_best_robust_score(self) -> None:
        evaluations = (
            _evaluation(1, expected=10.0, robust=0.0, win_rate=0.5),
            _evaluation(2, expected=8.0, robust=7.0, win_rate=0.6),
        )

        recommendation = RobustScoreMovePolicy().choose(evaluations)

        assert recommendation.recommended_action.card == Card.trump(2)

    def test_balanced_policy_can_shift_toward_robustness(self) -> None:
        evaluations = (
            _evaluation(1, expected=10.0, robust=2.0, win_rate=0.5),
            _evaluation(2, expected=9.0, robust=8.5, win_rate=0.6),
        )

        recommendation = BalancedMovePolicy(risk_weight=0.75).choose(evaluations)

        assert recommendation.recommended_action.card == Card.trump(2)
