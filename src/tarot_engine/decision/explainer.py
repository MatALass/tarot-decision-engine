"""Explainer: generate human-readable rationale for a decision recommendation.

Every sentence references a concrete number from the simulation results.
The explainer does not decide — it only describes a decision already made.
"""

from __future__ import annotations

from tarot_engine.decision.models import ContractEvaluation, RankedContract


def explain(
    best: ContractEvaluation,
    ranked: tuple[RankedContract, ...],
    policy_name: str,
) -> str:
    """Generate a plain-text rationale for the recommended contract.

    Args:
        best:        Evaluation of the recommended (rank-1) contract.
        ranked:      Full ranking, best → worst.
        policy_name: Name of the policy that produced this ranking.

    Returns:
        A multi-sentence string explaining the recommendation.
    """
    lines: list[str] = []
    lines.append(f"{best.contract.value} recommended by the {policy_name} policy.")
    lines.append(
        f"Win rate: {best.win_rate:.0%} over {best.n_simulations} simulations. "
        f"Expected score: {best.expected_score:+.0f} pts "
        f"(std: {best.score_std:.0f}, "
        f"range: {best.score_min:+d} to {best.score_max:+d})."
    )
    alternatives = [rc for rc in ranked if rc.rank > 1]
    if alternatives:
        lines.append(_explain_alternatives(best, alternatives, policy_name))
    return " ".join(lines)


def _explain_alternatives(
    best: ContractEvaluation,
    alternatives: list[RankedContract],
    policy_name: str,
) -> str:
    parts = [
        f"{rc.evaluation.contract.value}: {_alternative_reason(best, rc.evaluation, policy_name)}"
        for rc in alternatives
    ]
    return "Alternatives: " + "; ".join(parts) + "."


def _alternative_reason(
    best: ContractEvaluation,
    other: ContractEvaluation,
    policy_name: str,
) -> str:
    if policy_name == "conservative":
        if best.win_rate - other.win_rate > 0.001:
            return f"lower win rate ({other.win_rate:.0%} vs {best.win_rate:.0%})"
        return f"lower expected score ({other.expected_score:+.0f} pts)"

    if policy_name == "expected_value":
        if abs(best.expected_score - other.expected_score) > 0.5:
            return (
                f"lower expected score "
                f"({other.expected_score:+.0f} vs {best.expected_score:+.0f} pts)"
            )
        return f"lower win rate ({other.win_rate:.0%} vs {best.win_rate:.0%})"

    # balanced or unknown: explain on EV and risk
    ev_delta = best.expected_score - other.expected_score
    std_delta = other.score_std - best.score_std
    if ev_delta > 0.5 and std_delta > 0.5:
        return (
            f"lower expected score ({other.expected_score:+.0f} pts) "
            f"and higher risk (std {other.score_std:.0f} vs {best.score_std:.0f})"
        )
    if ev_delta > 0.5:
        return f"lower expected score ({other.expected_score:+.0f} vs {best.expected_score:+.0f} pts)"
    if std_delta > 0.5:
        return f"higher risk (std {other.score_std:.0f} vs {best.score_std:.0f})"
    return f"lower win rate ({other.win_rate:.0%} vs {best.win_rate:.0%})"
