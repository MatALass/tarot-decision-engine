"""Result objects for contract evaluation and decision recommendation."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.enums import Contract


@dataclass(frozen=True)
class ContractEvaluation:
    """Aggregated statistics for one contract over N simulations.

    score_std uses population standard deviation (pstdev): we treat the N
    simulations as the full empirical distribution being described.

    Invariants:
        0 ≤ win_rate ≤ 1
        n_simulations ≥ 1
        score_std ≥ 0
        score_min ≤ score_q10 ≤ score_q50 ≤ score_q90 ≤ score_max
        score_min ≤ expected_score ≤ score_max
    """

    contract: Contract
    n_simulations: int
    win_rate: float
    expected_score: float
    score_std: float
    score_min: int
    score_max: int
    score_q10: float
    score_q50: float
    score_q90: float

    def __post_init__(self) -> None:
        if self.n_simulations < 1:
            raise ValueError(f"n_simulations must be ≥ 1, got {self.n_simulations}.")
        if not (0.0 <= self.win_rate <= 1.0):
            raise ValueError(f"win_rate must be in [0, 1], got {self.win_rate}.")
        if self.score_std < 0:
            raise ValueError(f"score_std must be ≥ 0, got {self.score_std}.")
        if not (self.score_min <= self.score_q10 <= self.score_q50
                <= self.score_q90 <= self.score_max):
            raise ValueError(
                f"Quantile ordering violated: score_min ({self.score_min}) "
                f"≤ score_q10 ({self.score_q10}) ≤ score_q50 ({self.score_q50}) "
                f"≤ score_q90 ({self.score_q90}) ≤ score_max ({self.score_max})."
            )
        if not (self.score_min <= self.expected_score <= self.score_max):
            raise ValueError(
                f"expected_score ({self.expected_score}) must be in "
                f"[{self.score_min}, {self.score_max}]."
            )


@dataclass(frozen=True)
class RankedContract:
    """One contract in a ranked list. rank ≥ 1."""
    rank: int
    evaluation: ContractEvaluation

    def __post_init__(self) -> None:
        if self.rank < 1:
            raise ValueError(f"rank must be ≥ 1, got {self.rank}.")


@dataclass(frozen=True)
class DecisionRecommendation:
    """Output of a decision policy applied to a set of ContractEvaluations.

    Invariants:
        ranked_contracts non-empty
        recommended_contract matches rank-1 contract
        ranks are contiguous from 1
        each contract appears exactly once
    """

    recommended_contract: Contract
    policy_name: str
    ranked_contracts: tuple[RankedContract, ...]
    rationale: str
    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.ranked_contracts:
            raise ValueError("ranked_contracts must not be empty.")
        rank1 = self.ranked_contracts[0].evaluation.contract
        if rank1 != self.recommended_contract:
            raise ValueError(
                f"recommended_contract must match rank-1. "
                f"Got recommended={self.recommended_contract}, rank-1={rank1}."
            )
        ranks = [rc.rank for rc in self.ranked_contracts]
        expected = list(range(1, len(self.ranked_contracts) + 1))
        if ranks != expected:
            raise ValueError(
                f"ranked_contracts ranks must be contiguous from 1. "
                f"Got {ranks}, expected {expected}."
            )
        contracts = [rc.evaluation.contract for rc in self.ranked_contracts]
        seen: set[Contract] = set()
        duplicates: set[Contract] = set()
        for c in contracts:
            if c in seen:
                duplicates.add(c)
            seen.add(c)
        if duplicates:
            raise ValueError(
                f"Duplicate contracts in ranked_contracts: "
                f"{', '.join(c.value for c in duplicates)}."
            )
