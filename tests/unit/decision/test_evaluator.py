"""Tests for decision/evaluator.py."""

import statistics
import pytest
from tarot_engine.decision.evaluator import _quantile, evaluate_contract, evaluate_contracts
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.scoring import DealResult
from tarot_engine.simulation.monte_carlo import RawSimulationResults, SimulationConfig


def _raw(contract: Contract, scores: list[int], wins: list[bool]) -> RawSimulationResults:
    results = tuple(DealResult(taker_points=50.0, bout_count=1, contract=contract,
                               taker_won=w, score=s) for s, w in zip(scores, wins))
    return RawSimulationResults(contract=contract, deal_results=results,
                                config=SimulationConfig(n_simulations=max(len(scores),1), seed=0))


def _strong_hand() -> Hand:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    return Hand.from_cards(bouts + [c for c in deck if not c.is_bout][:12])


class TestQuantile:
    def test_median_odd(self) -> None: assert _quantile([1,2,3,4,5], 0.5) == 3.0
    def test_median_even(self) -> None: assert _quantile([1,2,3,4], 0.5) == 2.5
    def test_single(self) -> None: assert _quantile([42], 0.5) == 42.0
    def test_unsorted(self) -> None: assert _quantile([5,1,3,2,4], 0.5) == 3.0
    def test_invalid_q(self) -> None:
        with pytest.raises(ValueError): _quantile([1,2,3], -0.01)


class TestEvaluateContract:
    def test_win_rate(self) -> None:
        ev = evaluate_contract(_raw(Contract.GARDE, [100,-100,100,-100],[True,False,True,False]))
        assert ev.win_rate == pytest.approx(0.5)

    def test_expected_score(self) -> None:
        ev = evaluate_contract(_raw(Contract.GARDE, [100,200,300],[True,True,True]))
        assert ev.expected_score == pytest.approx(200.0)

    def test_uses_pstdev(self) -> None:
        scores = [100,-100,200,-200,50]
        ev = evaluate_contract(_raw(Contract.GARDE, scores, [True,False,True,False,True]))
        assert ev.score_std == pytest.approx(statistics.pstdev(scores))

    def test_invariants_always_satisfied(self) -> None:
        scores = [100,-200,300,-100,500,0,400,200,-300,150]
        wins = [True,False,True,False,True,False,True,True,False,True]
        ev = evaluate_contract(_raw(Contract.GARDE, scores, wins))
        assert 0 <= ev.win_rate <= 1
        assert ev.score_min <= ev.score_q10 <= ev.score_q50 <= ev.score_q90 <= ev.score_max
        assert ev.score_min <= ev.expected_score <= ev.score_max

    def test_zero_simulations_raises(self) -> None:
        with pytest.raises(ValueError): evaluate_contract(_raw(Contract.GARDE, [], []))


class TestEvaluateContracts:
    def test_returns_one_per_contract(self) -> None:
        config = SimulationConfig(n_simulations=10, seed=0)
        evals = evaluate_contracts(_strong_hand(), [Contract.PRISE, Contract.GARDE], config)
        assert len(evals) == 2

    def test_order_preserved(self) -> None:
        config = SimulationConfig(n_simulations=10, seed=0)
        contracts = list(Contract)
        evals = evaluate_contracts(_strong_hand(), contracts, config)
        assert [e.contract for e in evals] == contracts

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            evaluate_contracts(_strong_hand(), [], SimulationConfig(10, 0))

    def test_reproducible(self) -> None:
        config = SimulationConfig(n_simulations=20, seed=7)
        e1 = evaluate_contracts(_strong_hand(), list(Contract), config)
        e2 = evaluate_contracts(_strong_hand(), list(Contract), config)
        assert all(a.expected_score == b.expected_score for a, b in zip(e1, e2))
