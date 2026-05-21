"""Contract evaluator: aggregate raw simulation results into ContractEvaluation.

Separation of concerns:
  simulation/monte_carlo.py → RawSimulationResults  (raw scores)
  decision/evaluator.py     → ContractEvaluation    (aggregated statistics)
  decision/policies.py      → DecisionRecommendation (recommendation)
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence

from tarot_engine.decision.models import ContractEvaluation
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.simulation.monte_carlo import (
    RawSimulationResults,
    SimulationConfig,
    simulate_contract,
)


def evaluate_contract(results: RawSimulationResults) -> ContractEvaluation:
    """Aggregate raw simulation results into a ContractEvaluation.

    Raises:
        ValueError: If results contains no simulations.
    """
    if results.n == 0:
        raise ValueError("Cannot evaluate a contract with zero simulations.")

    scores = list(results.scores)
    wins = list(results.wins)
    n = results.n

    return ContractEvaluation(
        contract=results.contract,
        n_simulations=n,
        win_rate=sum(wins) / n,
        expected_score=sum(scores) / n,
        score_std=statistics.pstdev(scores),
        score_min=min(scores),
        score_max=max(scores),
        score_q10=_quantile(scores, 0.10),
        score_q50=_quantile(scores, 0.50),
        score_q90=_quantile(scores, 0.90),
    )


def evaluate_contracts(
    hand: Hand,
    contracts: Sequence[Contract],
    config: SimulationConfig,
) -> list[ContractEvaluation]:
    """Evaluate a sequence of contracts for a given hand.

    Each contract uses the same SimulationConfig. Sub-seeds are derived as
    config.seed + i, providing a form of common random numbers that reduces
    variance when comparing contracts.

    Raises:
        ValueError: If contracts is empty.
    """
    if not contracts:
        raise ValueError("Must provide at least one contract to evaluate.")
    return [evaluate_contract(simulate_contract(hand, c, config)) for c in contracts]


def _quantile(sorted_or_unsorted: list[int], q: float) -> float:
    """Compute the q-th quantile using linear interpolation (method R-7).

    Matches numpy's default quantile behaviour.

    Raises:
        ValueError: If q is outside [0, 1].
    """
    if not (0.0 <= q <= 1.0):
        raise ValueError(f"Quantile q must be in [0, 1], got {q}.")
    data = sorted(sorted_or_unsorted)
    n = len(data)
    if n == 1:
        return float(data[0])
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = lo + 1 if lo + 1 < n else lo
    frac = pos - lo
    if lo == hi:
        return float(data[lo])
    return float(data[lo]) * (1.0 - frac) + float(data[hi]) * frac
