"""Tarot scoring: bout threshold, deal score, contract result.

POINT THRESHOLDS
----------------
  0 bouts → 56 pts required
  1 bout  → 51 pts required
  2 bouts → 41 pts required
  3 bouts → 36 pts required

DEAL SCORE FORMULA
------------------
  margin = |taker_points - threshold|
  base   = margin + CONTRACT_BONUS (25)
  final  = round(base × contract.multiplier() × (N_PLAYERS - 1))
  signed = +final if taker won, -final if taker lost

ON ROUNDING
-----------
base may be a half-integer (0.5-pt cards). Multiplying fully before
round() ensures no intermediate rounding error. (N_PLAYERS - 1) = 4
always makes a half-integer base a whole number.

OUT OF SCOPE (MVP)
------------------
Poignée, Petit au bout, Chelem — addable as modifiers to `signed` later.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.deck import N_PLAYERS
from tarot_engine.domain.enums import Contract

CONTRACT_BONUS: int = 25

_REQUIRED_POINTS: dict[int, float] = {
    0: 56.0,
    1: 51.0,
    2: 41.0,
    3: 36.0,
}


def required_points(bout_count: int) -> float:
    """Return the minimum points the taker's camp must reach.

    Raises:
        ValueError: If bout_count is outside [0, 3].
    """
    if bout_count not in _REQUIRED_POINTS:
        raise ValueError(f"bout_count must be 0, 1, 2, or 3; got {bout_count}.")
    return _REQUIRED_POINTS[bout_count]


@dataclass(frozen=True)
class DealResult:
    """Outcome of a single simulated deal."""
    taker_points: float
    bout_count: int
    contract: Contract
    taker_won: bool
    score: int


def score_deal(
    taker_points: float,
    bout_count: int,
    contract: Contract,
) -> DealResult:
    """Compute the final score for a completed deal.

    Raises:
        ValueError: If bout_count is outside [0, 3].
    """
    threshold = required_points(bout_count)
    taker_won = taker_points >= threshold
    margin = abs(taker_points - threshold)
    base = margin + CONTRACT_BONUS
    final = round(base * contract.multiplier() * (N_PLAYERS - 1))
    signed = final if taker_won else -final
    return DealResult(
        taker_points=taker_points,
        bout_count=bout_count,
        contract=contract,
        taker_won=taker_won,
        score=signed,
    )
