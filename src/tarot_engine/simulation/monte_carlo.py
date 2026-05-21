"""Monte Carlo simulation loop.

Sub-seeds are derived as config.seed + i for simulation i, so simulation i
always produces the same deal regardless of n_simulations.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.scoring import DealResult
from tarot_engine.simulation.game_runner import run_deal
from tarot_engine.simulation.sampler import sample_deal
from tarot_engine.utils.random import make_rng


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for a Monte Carlo run."""
    n_simulations: int
    seed: int

    def __post_init__(self) -> None:
        if self.n_simulations < 1:
            raise ValueError(
                f"n_simulations must be at least 1, got {self.n_simulations}."
            )


@dataclass(frozen=True)
class RawSimulationResults:
    """Raw results from a Monte Carlo run for a single contract."""
    contract: Contract
    deal_results: tuple[DealResult, ...]
    config: SimulationConfig

    @property
    def n(self) -> int:
        return len(self.deal_results)

    @property
    def scores(self) -> tuple[int, ...]:
        return tuple(r.score for r in self.deal_results)

    @property
    def wins(self) -> tuple[bool, ...]:
        return tuple(r.taker_won for r in self.deal_results)


def simulate_contract(
    hand: Hand,
    contract: Contract,
    config: SimulationConfig,
) -> RawSimulationResults:
    """Run N Monte Carlo simulations for one hand + contract."""
    results: list[DealResult] = []
    for i in range(config.n_simulations):
        sim_rng = make_rng(config.seed + i)
        deal = sample_deal(hand, sim_rng)
        results.append(run_deal(deal, contract))
    return RawSimulationResults(
        contract=contract,
        deal_results=tuple(results),
        config=config,
    )
