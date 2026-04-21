"""Tests for move recommendation explanations."""

from tarot_engine.decision.move_explainer import explain_move
from tarot_engine.decision.move_policies import ExpectedScoreMovePolicy
from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.simulation.action_evaluator import ActionEvaluation


def _evaluation(card: Card, expected_score: float, win_rate: float, score_std: float, q10: float, q50: float, q90: float) -> ActionEvaluation:
    return ActionEvaluation(
        action=PlayAction(player_index=0, card=card),
        n_samples=10,
        win_rate=win_rate,
        expected_score=expected_score,
        score_std=score_std,
        score_min=int(q10 - 5),
        score_max=int(q90 + 5),
        score_q10=q10,
        score_q50=q50,
        score_q90=q90,
    )


class TestExplainMove:
    def test_summary_mentions_best_card_and_gap(self) -> None:
        policy = ExpectedScoreMovePolicy()
        recommendation = policy.choose((
            _evaluation(Card.trump(21), 12.0, 0.70, 4.0, 5.0, 12.0, 18.0),
            _evaluation(Card.trump(20), 9.0, 0.55, 5.0, 0.0, 9.0, 15.0),
        ))

        explanation = explain_move(recommendation)

        assert "T21" in explanation.summary
        assert explanation.top_gap_expected_score == 3.0
        assert explanation.alternatives_summary

    def test_single_action_mentions_only_legal_action(self) -> None:
        policy = ExpectedScoreMovePolicy()
        recommendation = policy.choose((
            _evaluation(Card.trump(1), 3.0, 0.40, 2.0, 1.0, 3.0, 6.0),
        ))

        explanation = explain_move(recommendation)

        assert explanation.top_gap_expected_score == 0.0
        assert "Only legal action" in explanation.summary
