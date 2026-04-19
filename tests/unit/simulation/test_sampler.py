"""Tests for simulation/sampler.py."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import DECK_SIZE, DOG_SIZE, HAND_SIZE, N_PLAYERS, generate_deck
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.domain.hand import Hand
from tarot_engine.simulation.sampler import _choose_called_king, sample_deal
from tarot_engine.utils.random import make_rng


def _strong_hand() -> Hand:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    fillers = [c for c in deck if not c.is_bout][:12]
    return Hand.from_cards(bouts + fillers)


class TestSampleDeal:
    def test_all_hands_correct_size(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        for h in deal.hands:
            assert len(h) == HAND_SIZE

    def test_dog_correct_size(self) -> None:
        assert len(sample_deal(_strong_hand(), make_rng(42)).dog) == DOG_SIZE

    def test_total_cards_equals_deck_size(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        all_cards = [c for h in deal.hands for c in h.cards] + list(deal.dog.cards)
        assert len(all_cards) == DECK_SIZE
        assert len(set(all_cards)) == DECK_SIZE

    def test_taker_hand_unchanged(self) -> None:
        hand = _strong_hand()
        deal = sample_deal(hand, make_rng(42))
        assert set(deal.hands[0].cards) == set(hand.cards)

    def test_called_king_is_roi(self) -> None:
        assert sample_deal(_strong_hand(), make_rng(42)).called_king.rank == Rank.ROI

    def test_partner_index_valid_or_none(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        if deal.partner_index is not None:
            assert 1 <= deal.partner_index <= N_PLAYERS - 1

    def test_partner_holds_called_king(self) -> None:
        deal = sample_deal(_strong_hand(), make_rng(42))
        if deal.partner_index is not None:
            assert deal.called_king in deal.hands[deal.partner_index]

    def test_reproducible(self) -> None:
        hand = _strong_hand()
        d1 = sample_deal(hand, make_rng(99))
        d2 = sample_deal(hand, make_rng(99))
        assert d1.dog.cards == d2.dog.cards

    def test_different_seeds_differ(self) -> None:
        hand = _strong_hand()
        assert sample_deal(hand, make_rng(1)).dog.cards != sample_deal(hand, make_rng(2)).dog.cards

    def test_no_contract_parameter(self) -> None:
        import inspect
        assert "contract" not in inspect.signature(sample_deal).parameters


class TestChooseCalledKing:
    def test_does_not_call_king_in_hand(self) -> None:
        deck = generate_deck()
        kh = Card.suited(Suit.HEARTS, Rank.ROI)
        fillers = [c for c in deck if c != kh and not c.is_excuse][:14]
        hand = Hand.from_cards([kh] + fillers)
        assert _choose_called_king(hand) != kh

    def test_prefers_void_suit_king(self) -> None:
        deck = generate_deck()
        # Build a hand with at least one card in Spades, Hearts, Diamonds
        # but no Clubs — so only Clubs is void, and KC should be called.
        spades  = [c for c in deck if c.suit == Suit.SPADES  and c.rank != Rank.ROI][:3]
        hearts  = [c for c in deck if c.suit == Suit.HEARTS  and c.rank != Rank.ROI][:3]
        diamonds = [c for c in deck if c.suit == Suit.DIAMONDS and c.rank != Rank.ROI][:3]
        trumps  = [c for c in deck if c.is_trump and not c.is_bout][:5]
        hand = Hand.from_cards(spades + hearts + diamonds + trumps + [Card.excuse()])
        called = _choose_called_king(hand)
        assert called.suit == Suit.CLUBS

    def test_fallback_all_kings_in_hand(self) -> None:
        deck = generate_deck()
        kings = [Card.suited(s, Rank.ROI) for s in Suit]
        fillers = [c for c in deck if c.rank != Rank.ROI and not c.is_trump and not c.is_excuse][:11]
        hand = Hand.from_cards(kings + fillers)
        assert _choose_called_king(hand).rank == Rank.ROI
