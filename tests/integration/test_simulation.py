"""Integration tests: full simulation pipeline."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.simulation.monte_carlo import SimulationConfig, simulate_contract


def _strong_hand() -> Hand:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    fillers = [c for c in deck if not c.is_bout][:12]
    return Hand.from_cards(bouts + fillers)


def _weak_hand() -> Hand:
    deck = generate_deck()
    suited = [c for c in deck if c.suit is not None and not c.is_bout][:15]
    return Hand.from_cards(suited)


class TestSimulateContract:
    def test_correct_number_of_results(self) -> None:
        config = SimulationConfig(n_simulations=10, seed=42)
        results = simulate_contract(_strong_hand(), Contract.GARDE, config)
        assert results.n == 10

    def test_all_scores_are_integers(self) -> None:
        config = SimulationConfig(n_simulations=20, seed=0)
        results = simulate_contract(_strong_hand(), Contract.PRISE, config)
        for score in results.scores:
            assert isinstance(score, int)

    def test_reproducible_with_same_seed(self) -> None:
        config = SimulationConfig(n_simulations=50, seed=7)
        r1 = simulate_contract(_strong_hand(), Contract.GARDE, config)
        r2 = simulate_contract(_strong_hand(), Contract.GARDE, config)
        assert r1.scores == r2.scores
        assert r1.wins == r2.wins

    def test_different_seeds_give_different_results(self) -> None:
        r1 = simulate_contract(_strong_hand(), Contract.GARDE, SimulationConfig(20, seed=1))
        r2 = simulate_contract(_strong_hand(), Contract.GARDE, SimulationConfig(20, seed=2))
        assert r1.scores != r2.scores

    def test_strong_hand_wins_more_than_weak(self) -> None:
        config = SimulationConfig(n_simulations=200, seed=42)
        strong = simulate_contract(_strong_hand(), Contract.PRISE, config)
        weak   = simulate_contract(_weak_hand(),   Contract.PRISE, config)
        assert sum(strong.wins) / strong.n > sum(weak.wins) / weak.n

    def test_win_rate_in_valid_range(self) -> None:
        config = SimulationConfig(n_simulations=100, seed=0)
        results = simulate_contract(_strong_hand(), Contract.GARDE, config)
        assert 0.0 <= sum(results.wins) / results.n <= 1.0

    def test_zero_simulations_rejected(self) -> None:
        with pytest.raises(ValueError, match="n_simulations"):
            SimulationConfig(n_simulations=0, seed=42)

    def test_all_contracts_run_without_error(self) -> None:
        config = SimulationConfig(n_simulations=10, seed=42)
        for contract in Contract:
            results = simulate_contract(_strong_hand(), contract, config)
            assert results.n == 10
