"""Tests for domain enums: Contract, Suit, Rank, PlayerRole, BidAction."""

import pytest

from tarot_engine.domain.enums import BidAction, Contract, PlayerRole, Rank, Suit


class TestContract:
    def test_all_contracts_are_defined(self) -> None:
        names = {c.value for c in Contract}
        assert names == {"PRISE", "GARDE", "GARDE_SANS", "GARDE_CONTRE"}

    def test_pass_is_not_a_contract(self) -> None:
        """Critical: PASS must not exist in Contract."""
        assert not any(c.value == "PASS" for c in Contract)

    def test_multipliers_are_strictly_increasing(self) -> None:
        ordered = [Contract.PRISE, Contract.GARDE, Contract.GARDE_SANS, Contract.GARDE_CONTRE]
        multipliers = [c.multiplier() for c in ordered]
        assert multipliers == sorted(multipliers), "Multipliers must increase with contract difficulty"
        assert multipliers == [1, 2, 4, 6]

    def test_uses_dog(self) -> None:
        assert Contract.PRISE.uses_dog() is True
        assert Contract.GARDE.uses_dog() is True
        assert Contract.GARDE_SANS.uses_dog() is False
        assert Contract.GARDE_CONTRE.uses_dog() is False

    def test_dog_counts_for_taker(self) -> None:
        assert Contract.PRISE.dog_counts_for_taker() is True
        assert Contract.GARDE.dog_counts_for_taker() is True
        assert Contract.GARDE_SANS.dog_counts_for_taker() is True
        assert Contract.GARDE_CONTRE.dog_counts_for_taker() is False


class TestBidAction:
    def test_pass_exists_in_bid_action(self) -> None:
        assert BidAction.PASS in BidAction

    def test_pass_is_not_a_contract(self) -> None:
        assert BidAction.PASS.is_contract() is False

    def test_all_non_pass_are_contracts(self) -> None:
        for action in BidAction:
            if action != BidAction.PASS:
                assert action.is_contract() is True

    def test_to_contract_raises_on_pass(self) -> None:
        with pytest.raises(ValueError, match="PASS"):
            BidAction.PASS.to_contract()

    def test_to_contract_maps_correctly(self) -> None:
        mapping = {
            BidAction.PRISE: Contract.PRISE,
            BidAction.GARDE: Contract.GARDE,
            BidAction.GARDE_SANS: Contract.GARDE_SANS,
            BidAction.GARDE_CONTRE: Contract.GARDE_CONTRE,
        }
        for bid, contract in mapping.items():
            assert bid.to_contract() == contract

    def test_bid_action_and_contract_share_same_non_pass_values(self) -> None:
        """BidAction values (except PASS) must match Contract values exactly."""
        bid_values = {a.value for a in BidAction if a != BidAction.PASS}
        contract_values = {c.value for c in Contract}
        assert bid_values == contract_values

    def test_player_role_has_three_roles(self) -> None:
        assert len(list(PlayerRole)) == 3
        roles = {PlayerRole.TAKER, PlayerRole.PARTNER, PlayerRole.DEFENDER}
        assert set(PlayerRole) == roles

    def test_suit_has_four_suits(self) -> None:
        assert len(list(Suit)) == 4

    def test_rank_has_fourteen_ranks(self) -> None:
        assert len(list(Rank)) == 14
