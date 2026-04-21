"""Human-readable explanations for move recommendations."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.simulation.action_evaluator import ActionEvaluation, MoveRecommendation
from tarot_engine.utils.parsing import format_card_token


@dataclass(frozen=True)
class MoveExplanation:
    """Structured explanation for a move recommendation."""

    summary: str
    top_gap_expected_score: float
    top_gap_win_rate: float
    risk_comment: str
    alternatives_summary: tuple[str, ...]



def explain_move(recommendation: MoveRecommendation) -> MoveExplanation:
    """Generate a structured explanation from ranked move evaluations."""
    ranked = recommendation.ranked_actions
    best = ranked[0].evaluation
    second = ranked[1].evaluation if len(ranked) > 1 else None

    top_gap_expected_score = (
        best.expected_score - second.expected_score if second is not None else 0.0
    )
    top_gap_win_rate = best.win_rate - second.win_rate if second is not None else 0.0

    risk_comment = _risk_comment(best)
    summary = _summary(best, second, recommendation.policy_name, risk_comment)
    alternatives = tuple(
        _alternative_summary(best, ranked_action.evaluation)
        for ranked_action in ranked[1:]
    )
    return MoveExplanation(
        summary=summary,
        top_gap_expected_score=top_gap_expected_score,
        top_gap_win_rate=top_gap_win_rate,
        risk_comment=risk_comment,
        alternatives_summary=alternatives,
    )



def _summary(
    best: ActionEvaluation,
    second: ActionEvaluation | None,
    policy_name: str,
    risk_comment: str,
) -> str:
    card = format_card_token(best.action.card)
    if second is None:
        return (
            f"Only legal action available: play {card}. "
            f"Expected score {best.expected_score:+.2f}; win rate {best.win_rate:.1%}. {risk_comment}"
        )
    return (
        f"{card} is recommended by the {policy_name} policy. "
        f"Expected score {best.expected_score:+.2f} vs {second.expected_score:+.2f} for the next best action "
        f"(gap {best.expected_score - second.expected_score:+.2f}). "
        f"Win rate {best.win_rate:.1%} vs {second.win_rate:.1%}. {risk_comment}"
    )



def _risk_comment(best: ActionEvaluation) -> str:
    interdecile = best.score_q90 - best.score_q10
    if interdecile <= 15:
        return f"Low dispersion profile (Q10 {best.score_q10:+.1f}, Q90 {best.score_q90:+.1f})."
    if interdecile <= 35:
        return f"Moderate dispersion profile (Q10 {best.score_q10:+.1f}, Q90 {best.score_q90:+.1f})."
    return f"High dispersion profile (Q10 {best.score_q10:+.1f}, Q90 {best.score_q90:+.1f})."



def _alternative_summary(best: ActionEvaluation, other: ActionEvaluation) -> str:
    card = format_card_token(other.action.card)
    delta_ev = best.expected_score - other.expected_score
    delta_wr = best.win_rate - other.win_rate
    delta_std = other.score_std - best.score_std
    reasons: list[str] = []
    if abs(delta_ev) >= 0.5:
        reasons.append(f"EV lower by {delta_ev:+.2f}")
    if abs(delta_wr) >= 0.01:
        reasons.append(f"win rate lower by {delta_wr:+.1%}")
    if delta_std >= 0.5:
        reasons.append(f"more volatile by {delta_std:+.2f} std")
    if not reasons:
        reasons.append("strictly behind on tie-break order")
    return f"{card}: " + ", ".join(reasons)
