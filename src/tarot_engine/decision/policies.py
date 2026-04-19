"""Decision policies: select the best contract from a set of evaluations.

POLICIES
--------
ConservativePolicy    — maximise win_rate
ExpectedValuePolicy   — maximise expected_score
BalancedPolicy        — maximise (expected_score - risk_weight * score_std)

TIE-BREAK
---------
All policies break ties by preferring the contract with the lower multiplier
(smaller stakes = safer default when contracts are otherwise equal).
Sort keys are expressed as ascending tuples with negated primary/secondary
criteria, making tie-break direction explicit without reverse=True.

WARNINGS
--------
- Win rate < WIN_RATE_CAUTION_THRESHOLD (0.40): low win rate notice.
- Top-two primary scores within CLOSE_CALL_THRESHOLD (5% relative): close call.
"""

from __future__ import annotations

from typing import Protocol

from tarot_engine.decision.explainer import explain
from tarot_engine.decision.models import (
    ContractEvaluation,
    DecisionRecommendation,
    RankedContract,
)

WIN_RATE_CAUTION_THRESHOLD: float = 0.40
CLOSE_CALL_THRESHOLD: float = 0.05


class DecisionPolicy(Protocol):
    @property
    def name(self) -> str: ...
    def choose(self, evaluations: list[ContractEvaluation]) -> DecisionRecommendation: ...


def _validate(evaluations: list[ContractEvaluation]) -> None:
    if not evaluations:
        raise ValueError("evaluations must not be empty.")


def _build_recommendation(
    sorted_evals: list[ContractEvaluation],
    policy_name: str,
    primary_scores: list[float],
) -> DecisionRecommendation:
    ranked = tuple(
        RankedContract(rank=i + 1, evaluation=ev)
        for i, ev in enumerate(sorted_evals)
    )
    warnings = _generate_warnings(sorted_evals[0], sorted_evals, primary_scores)
    rationale = explain(sorted_evals[0], ranked, policy_name)
    return DecisionRecommendation(
        recommended_contract=sorted_evals[0].contract,
        policy_name=policy_name,
        ranked_contracts=ranked,
        rationale=rationale,
        warnings=tuple(warnings),
    )


def _generate_warnings(
    best: ContractEvaluation,
    sorted_evals: list[ContractEvaluation],
    primary_scores: list[float],
) -> list[str]:
    warnings: list[str] = []
    if best.win_rate < WIN_RATE_CAUTION_THRESHOLD:
        warnings.append(
            f"{best.contract.value} has a low win rate "
            f"({best.win_rate:.0%} across {best.n_simulations} simulations)."
        )
    if len(sorted_evals) >= 2:
        best_score = primary_scores[0]
        second_score = primary_scores[1]
        scale = abs(best_score) if abs(best_score) > 1e-9 else 1.0
        if abs(best_score - second_score) / scale < CLOSE_CALL_THRESHOLD:
            warnings.append(
                f"Close call between {best.contract.value} and "
                f"{sorted_evals[1].contract.value}: the difference on the primary "
                f"criterion is small."
            )
    return warnings


class ConservativePolicy:
    """Maximise win_rate. Ties: expected_score DESC, multiplier ASC."""

    @property
    def name(self) -> str:
        return "conservative"

    def choose(self, evaluations: list[ContractEvaluation]) -> DecisionRecommendation:
        _validate(evaluations)
        sorted_evals = sorted(
            evaluations,
            key=lambda ev: (-ev.win_rate, -ev.expected_score, ev.contract.multiplier()),
        )
        return _build_recommendation(sorted_evals, self.name,
                                     [ev.win_rate for ev in sorted_evals])


class ExpectedValuePolicy:
    """Maximise expected_score. Ties: win_rate DESC, multiplier ASC."""

    @property
    def name(self) -> str:
        return "expected_value"

    def choose(self, evaluations: list[ContractEvaluation]) -> DecisionRecommendation:
        _validate(evaluations)
        sorted_evals = sorted(
            evaluations,
            key=lambda ev: (-ev.expected_score, -ev.win_rate, ev.contract.multiplier()),
        )
        return _build_recommendation(sorted_evals, self.name,
                                     [ev.expected_score for ev in sorted_evals])


class BalancedPolicy:
    """Maximise utility = expected_score - risk_weight * score_std.

    Args:
        risk_weight: Non-negative weight penalising variance. Default 0.5.
    """

    def __init__(self, risk_weight: float = 0.5) -> None:
        if risk_weight < 0:
            raise ValueError(f"risk_weight must be ≥ 0, got {risk_weight}.")
        self._risk_weight = risk_weight

    @property
    def name(self) -> str:
        return f"balanced(risk_weight={self._risk_weight})"

    def utility(self, ev: ContractEvaluation) -> float:
        return ev.expected_score - self._risk_weight * ev.score_std

    def choose(self, evaluations: list[ContractEvaluation]) -> DecisionRecommendation:
        _validate(evaluations)
        sorted_evals = sorted(
            evaluations,
            key=lambda ev: (-self.utility(ev), -ev.win_rate, ev.contract.multiplier()),
        )
        return _build_recommendation(sorted_evals, self.name,
                                     [self.utility(ev) for ev in sorted_evals])
