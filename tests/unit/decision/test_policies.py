"""Tests for decision/policies.py."""

import pytest
from tarot_engine.decision.models import ContractEvaluation
from tarot_engine.decision.policies import (BalancedPolicy, ConservativePolicy,
                                             ExpectedValuePolicy, WIN_RATE_CAUTION_THRESHOLD)
from tarot_engine.domain.enums import Contract


def _ev(contract: Contract, win_rate: float, expected_score: float,
        score_std: float = 50.0) -> ContractEvaluation:
    return ContractEvaluation(contract=contract, n_simulations=100,
                              win_rate=win_rate, expected_score=expected_score,
                              score_std=score_std, score_min=-200, score_max=400,
                              score_q10=-100.0, score_q50=100.0, score_q90=300.0)


ALL = [_ev(Contract.PRISE, 0.70, 80.0), _ev(Contract.GARDE, 0.55, 120.0),
       _ev(Contract.GARDE_SANS, 0.30, 200.0, 150.0), _ev(Contract.GARDE_CONTRE, 0.20, 250.0, 220.0)]


def _check(rec: object) -> None:
    from tarot_engine.decision.models import DecisionRecommendation
    assert isinstance(rec, DecisionRecommendation)
    assert rec.ranked_contracts[0].evaluation.contract == rec.recommended_contract
    ranks = [rc.rank for rc in rec.ranked_contracts]
    assert ranks == list(range(1, len(ranks)+1))


class TestConservativePolicy:
    p = ConservativePolicy()
    def test_name(self) -> None: assert self.p.name == "conservative"
    def test_selects_highest_win_rate(self) -> None:
        assert self.p.choose(ALL).recommended_contract == Contract.PRISE
    def test_descending_win_rate(self) -> None:
        rec = self.p.choose(ALL)
        wr = [rc.evaluation.win_rate for rc in rec.ranked_contracts]
        assert wr == sorted(wr, reverse=True)
    def test_invariants(self) -> None: _check(self.p.choose(ALL))
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError): self.p.choose([])
    def test_low_win_rate_warning(self) -> None:
        low = _ev(Contract.PRISE, WIN_RATE_CAUTION_THRESHOLD - 0.01, 50.0)
        rec = self.p.choose([low])
        assert any("low win rate" in w.lower() for w in rec.warnings)
    def test_no_passing_mention(self) -> None:
        low = _ev(Contract.PRISE, WIN_RATE_CAUTION_THRESHOLD - 0.01, 50.0)
        assert not any("passing" in w.lower() for w in self.p.choose([low]).warnings)
    def test_tie_broken_by_ev(self) -> None:
        a = _ev(Contract.PRISE, 0.60, 100.0)
        b = _ev(Contract.GARDE, 0.60, 150.0)
        assert self.p.choose([a, b]).recommended_contract == Contract.GARDE
    def test_tie_broken_by_lower_multiplier(self) -> None:
        a = _ev(Contract.PRISE, 0.60, 100.0)
        b = _ev(Contract.GARDE, 0.60, 100.0)
        assert self.p.choose([a, b]).recommended_contract == Contract.PRISE


class TestExpectedValuePolicy:
    p = ExpectedValuePolicy()
    def test_name(self) -> None: assert self.p.name == "expected_value"
    def test_selects_highest_ev(self) -> None:
        assert self.p.choose(ALL).recommended_contract == Contract.GARDE_CONTRE
    def test_invariants(self) -> None: _check(self.p.choose(ALL))
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError): self.p.choose([])


class TestBalancedPolicy:
    p = BalancedPolicy(risk_weight=0.5)
    def test_name(self) -> None: assert "0.5" in self.p.name
    def test_utility_formula(self) -> None:
        ev = _ev(Contract.GARDE, 0.60, 200.0, 100.0)
        assert self.p.utility(ev) == pytest.approx(150.0)
    def test_high_risk_weight_penalises_variance(self) -> None:
        hrp = BalancedPolicy(risk_weight=2.0)
        a = _ev(Contract.GARDE_SANS, 0.55, 200.0, 200.0)  # utility=-200
        b = _ev(Contract.PRISE, 0.65, 150.0, 10.0)         # utility=130
        assert hrp.choose([a, b]).recommended_contract == Contract.PRISE
    def test_negative_risk_weight_raises(self) -> None:
        with pytest.raises(ValueError): BalancedPolicy(risk_weight=-0.1)
    def test_invariants(self) -> None: _check(self.p.choose(ALL))
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError): self.p.choose([])
