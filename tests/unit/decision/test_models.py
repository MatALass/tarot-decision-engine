"""Tests for decision/models.py."""

import pytest
from tarot_engine.decision.models import ContractEvaluation, DecisionRecommendation, RankedContract
from tarot_engine.domain.enums import Contract


def _eval(contract: Contract = Contract.GARDE, **kw: object) -> ContractEvaluation:
    defaults = dict(n_simulations=100, win_rate=0.6, expected_score=150.0,
                    score_std=80.0, score_min=-300, score_max=600,
                    score_q10=-120.0, score_q50=160.0, score_q90=400.0)
    defaults.update(kw)
    return ContractEvaluation(contract=contract, **defaults)  # type: ignore[arg-type]


class TestContractEvaluationInvariants:
    def test_valid(self) -> None: _eval()
    def test_win_rate_below_zero(self) -> None:
        with pytest.raises(ValueError): _eval(win_rate=-0.01)
    def test_win_rate_above_one(self) -> None:
        with pytest.raises(ValueError): _eval(win_rate=1.01)
    def test_zero_simulations(self) -> None:
        with pytest.raises(ValueError): _eval(n_simulations=0)
    def test_negative_std(self) -> None:
        with pytest.raises(ValueError): _eval(score_std=-1.0)
    def test_q10_above_q50(self) -> None:
        with pytest.raises(ValueError): _eval(score_q10=300.0, score_q50=100.0)
    def test_q90_above_max(self) -> None:
        with pytest.raises(ValueError): _eval(score_max=600, score_q90=700.0)
    def test_expected_below_min(self) -> None:
        with pytest.raises(ValueError): _eval(score_min=-300, expected_score=-400.0)
    def test_frozen(self) -> None:
        with pytest.raises((AttributeError, TypeError)): _eval().win_rate = 0.5  # type: ignore[misc]


class TestRankedContract:
    def test_rank_one_valid(self) -> None: RankedContract(rank=1, evaluation=_eval())
    def test_rank_zero_raises(self) -> None:
        with pytest.raises(ValueError): RankedContract(rank=0, evaluation=_eval())
    def test_rank_negative_raises(self) -> None:
        with pytest.raises(ValueError): RankedContract(rank=-1, evaluation=_eval())


class TestDecisionRecommendation:
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            DecisionRecommendation(recommended_contract=Contract.GARDE,
                                   policy_name="x", ranked_contracts=(),
                                   rationale="x", warnings=())

    def test_mismatch_raises(self) -> None:
        rc = RankedContract(rank=1, evaluation=_eval(Contract.PRISE))
        with pytest.raises(ValueError):
            DecisionRecommendation(recommended_contract=Contract.GARDE,
                                   policy_name="x", ranked_contracts=(rc,),
                                   rationale="x", warnings=())

    def test_non_contiguous_raises(self) -> None:
        rc1 = RankedContract(rank=1, evaluation=_eval(Contract.GARDE))
        rc3 = RankedContract(rank=3, evaluation=_eval(Contract.PRISE))
        with pytest.raises(ValueError):
            DecisionRecommendation(recommended_contract=Contract.GARDE,
                                   policy_name="x", ranked_contracts=(rc1, rc3),
                                   rationale="x", warnings=())

    def test_duplicate_contracts_raises(self) -> None:
        rc1 = RankedContract(rank=1, evaluation=_eval(Contract.GARDE))
        rc2 = RankedContract(rank=2, evaluation=_eval(Contract.GARDE))
        with pytest.raises(ValueError):
            DecisionRecommendation(recommended_contract=Contract.GARDE,
                                   policy_name="x", ranked_contracts=(rc1, rc2),
                                   rationale="x", warnings=())
