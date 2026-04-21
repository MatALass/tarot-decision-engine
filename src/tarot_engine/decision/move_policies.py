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
                key=lambda ev: (-ev.expected_score, -ev.robust_score, -ev.win_rate, str(ev.action.card)),
            )
        )
        ranked = tuple(
            RankedAction(rank=index + 1, evaluation=evaluation)
            for index, evaluation in enumerate(sorted_evaluations)
        )
        best = sorted_evaluations[0]
        rationale = (
            f"Best EV: {best.expected_score:.2f}; "
            f"robust score {best.robust_score:.2f}; "
            f"win rate {best.win_rate:.1%}; "
            f"std {best.score_std:.2f}."
        )
        return MoveRecommendation(
            recommended_action=best.action,
            policy_name=self.name,
            ranked_actions=ranked,
            rationale=rationale,
        )


class RobustScoreMovePolicy:
    """Choose the action with the best lower-tail outcome."""

    @property
    def name(self) -> str:
        return "robust_score"

    def choose(self, evaluations: tuple[ActionEvaluation, ...]) -> MoveRecommendation:
        if not evaluations:
            raise ValueError("evaluations must not be empty.")
        sorted_evaluations = tuple(
            sorted(
                evaluations,
                key=lambda ev: (-ev.robust_score, -ev.expected_score, -ev.win_rate, str(ev.action.card)),
            )
        )
        ranked = tuple(
            RankedAction(rank=index + 1, evaluation=evaluation)
            for index, evaluation in enumerate(sorted_evaluations)
        )
        best = sorted_evaluations[0]
        rationale = (
            f"Best robust score: {best.robust_score:.2f}; "
            f"EV {best.expected_score:.2f}; "
            f"downside risk {best.downside_risk:.2f}; "
            f"win rate {best.win_rate:.1%}."
        )
        return MoveRecommendation(
            recommended_action=best.action,
            policy_name=self.name,
            ranked_actions=ranked,
            rationale=rationale,
        )


class BalancedMovePolicy:
    """Trade off expected value and robustness."""

    def __init__(self, risk_weight: float = 0.5) -> None:
        if not (0.0 <= risk_weight <= 1.0):
            raise ValueError(f"risk_weight must be in [0, 1], got {risk_weight}.")
        self.risk_weight = risk_weight

    @property
    def name(self) -> str:
        return "balanced"

    def choose(self, evaluations: tuple[ActionEvaluation, ...]) -> MoveRecommendation:
        if not evaluations:
            raise ValueError("evaluations must not be empty.")
        sorted_evaluations = tuple(
            sorted(
                evaluations,
                key=lambda ev: (
                    -self._balanced_score(ev),
                    -ev.expected_score,
                    -ev.robust_score,
                    -ev.win_rate,
                    str(ev.action.card),
                ),
            )
        )
        ranked = tuple(
            RankedAction(rank=index + 1, evaluation=evaluation)
            for index, evaluation in enumerate(sorted_evaluations)
        )
        best = sorted_evaluations[0]
        rationale = (
            f"Best balanced score: {self._balanced_score(best):.2f}; "
            f"EV {best.expected_score:.2f}; "
            f"robust score {best.robust_score:.2f}; "
            f"risk weight {self.risk_weight:.2f}."
        )
        return MoveRecommendation(
            recommended_action=best.action,
            policy_name=self.name,
            ranked_actions=ranked,
            rationale=rationale,
        )

    def _balanced_score(self, evaluation: ActionEvaluation) -> float:
        return ((1.0 - self.risk_weight) * evaluation.expected_score) + (
            self.risk_weight * evaluation.robust_score
        )
