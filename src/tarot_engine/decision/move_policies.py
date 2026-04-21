"""Decision policies for turn-by-turn action recommendations."""

from __future__ import annotations

from typing import Protocol

from tarot_engine.simulation.action_evaluator import (
    ActionEvaluation,
    MoveRecommendation,
    RankedAction,
)


class MoveDecisionPolicy(Protocol):
    @property
    def name(self) -> str: ...
    def choose(self, evaluations: tuple[ActionEvaluation, ...]) -> MoveRecommendation: ...


class ExpectedScoreMovePolicy:
    """Choose the action with the highest expected score."""

    @property
    def name(self) -> str:
        return "expected_score"

    def choose(self, evaluations: tuple[ActionEvaluation, ...]) -> MoveRecommendation:
        if not evaluations:
            raise ValueError("evaluations must not be empty.")
        sorted_evaluations = tuple(
            sorted(
                evaluations,
                key=lambda ev: (-ev.expected_score, -ev.win_rate, str(ev.action.card)),
            )
        )
        ranked = tuple(
            RankedAction(rank=index + 1, evaluation=evaluation)
            for index, evaluation in enumerate(sorted_evaluations)
        )
        best = sorted_evaluations[0]
        rationale = (
            f"Best EV: {best.expected_score:.2f}; "
            f"win rate {best.win_rate:.1%}; "
            f"std {best.score_std:.2f}."
        )
        return MoveRecommendation(
            recommended_action=best.action,
            policy_name=self.name,
            ranked_actions=ranked,
            rationale=rationale,
        )
