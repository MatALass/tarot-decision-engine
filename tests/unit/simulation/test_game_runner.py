"""Tests for simulation/game_runner.py."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import HAND_SIZE, generate_deck
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.scoring import DealResult
from tarot_engine.simulation.game_runner import (
    _PlayerState,
    _apply_dog_exchange,
    _select_discards,
    run_deal,
)
from tarot_engine.simulation.sampler import sample_deal
from tarot_engine.utils.random import make_rng


def _strong_hand() -> Hand:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    fillers = [c for c in deck if not c.is_bout][:12]
    return Hand.from_cards(bouts + fillers)


class TestSelectDiscards:
    def test_returns_exactly_three(self) -> None:
        hand = list(generate_deck()[:18])
        assert len(_select_discards(hand, n=3)) == 3

    def test_never_discards_bouts(self) -> None:
        hand = list(generate_deck()[:18])
        for card in _select_discards(hand, n=3):
            assert not card.is_bout and not card.is_excuse

    def test_no_duplicates(self) -> None:
        hand = list(generate_deck()[:18])
        discards = _select_discards(hand, n=3)
        assert len(set(discards)) == 3

    def test_all_from_hand(self) -> None:
        hand = list(generate_deck()[:18])
        hand_set = set(hand)
        for card in _select_discards(hand, n=3):
            assert card in hand_set


class TestApplyDogExchange:
    def test_taker_has_exactly_hand_size_after_exchange(self) -> None:
        deck = generate_deck()
        state = _PlayerState(index=0, hand=list(deck[:HAND_SIZE]))
        _apply_dog_exchange(state, list(deck[HAND_SIZE: HAND_SIZE + 3]))
        assert len(state.hand) == HAND_SIZE

    def test_discards_go_to_won_cards(self) -> None:
        deck = generate_deck()
        state = _PlayerState(index=0, hand=list(deck[:HAND_SIZE]))
        _apply_dog_exchange(state, list(deck[HAND_SIZE: HAND_SIZE + 3]))
        assert len(state.won_cards) == 3

    def test_no_card_lost(self) -> None:
        deck = generate_deck()
        taker_cards = list(deck[:HAND_SIZE])
        dog_cards = list(deck[HAND_SIZE: HAND_SIZE + 3])
        original = set(taker_cards + dog_cards)
        state = _PlayerState(index=0, hand=taker_cards)
        _apply_dog_exchange(state, dog_cards)
        assert set(state.hand + state.won_cards) == original

    def test_no_bout_discarded(self) -> None:
        deck = generate_deck()
        bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
        fillers = [c for c in deck if not c.is_bout][:12]
        dog_cards = [c for c in deck if c not in set(bouts + fillers)][:3]
        state = _PlayerState(index=0, hand=bouts + fillers)
        _apply_dog_exchange(state, dog_cards)
        for card in state.won_cards:
            assert not card.is_bout and not card.is_excuse


class TestRunDeal:
    def test_returns_deal_result(self) -> None:
        hand = _strong_hand()
        deal = sample_deal(hand, make_rng(42))
        assert isinstance(run_deal(deal, Contract.GARDE), DealResult)

    def test_bout_count_in_range(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        assert 0 <= run_deal(deal, Contract.GARDE).bout_count <= 3

    def test_taker_points_in_range(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        assert 0 <= run_deal(deal, Contract.GARDE).taker_points <= 91

    def test_all_contracts_run(self) -> None:
        hand = _strong_hand()
        for contract in Contract:
            run_deal(sample_deal(hand, make_rng(0)), contract)

    def test_reproducible(self) -> None:
        hand = _strong_hand()
        r1 = run_deal(sample_deal(hand, make_rng(7)), Contract.GARDE)
        r2 = run_deal(sample_deal(hand, make_rng(7)), Contract.GARDE)
        assert r1.score == r2.score
