"""Tests for deck generation and validation."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import (
    DECK_SIZE,
    DOG_SIZE,
    HAND_SIZE,
    N_PLAYERS,
    generate_deck,
    validate_deck,
)
from tarot_engine.domain.enums import Rank, Suit


class TestGenerateDeck:
    def test_deck_has_correct_size(self) -> None:
        assert len(generate_deck()) == DECK_SIZE

    def test_deck_has_exactly_one_excuse(self) -> None:
        deck = generate_deck()
        excuses = [c for c in deck if c.is_excuse]
        assert len(excuses) == 1

    def test_deck_has_21_trumps(self) -> None:
        deck = generate_deck()
        trumps = [c for c in deck if c.is_trump]
        assert len(trumps) == 21

    def test_deck_has_all_trump_values(self) -> None:
        deck = generate_deck()
        trump_values = {c.trump_value for c in deck if c.is_trump}
        assert trump_values == set(range(1, 22))

    def test_deck_has_56_suited_cards(self) -> None:
        deck = generate_deck()
        suited = [c for c in deck if c.suit is not None]
        assert len(suited) == 56

    def test_deck_has_14_cards_per_suit(self) -> None:
        deck = generate_deck()
        for suit in Suit:
            suited = [c for c in deck if c.suit == suit]
            assert len(suited) == 14, f"Expected 14 cards for {suit}, got {len(suited)}"

    def test_deck_has_all_ranks_per_suit(self) -> None:
        deck = generate_deck()
        for suit in Suit:
            ranks = {c.rank for c in deck if c.suit == suit}
            assert ranks == set(Rank)

    def test_deck_has_no_duplicates(self) -> None:
        deck = generate_deck()
        assert len(set(deck)) == len(deck)

    def test_deck_is_tuple(self) -> None:
        assert isinstance(generate_deck(), tuple)

    def test_deck_is_deterministic(self) -> None:
        assert generate_deck() == generate_deck()

    def test_deck_distribution_constants(self) -> None:
        """5 players × 15 cards + 3 dog = 78 cards."""
        assert N_PLAYERS * HAND_SIZE + DOG_SIZE == DECK_SIZE == 78


class TestValidateDeck:
    def test_valid_deck_passes(self) -> None:
        validate_deck(generate_deck())  # must not raise

    def test_wrong_size_raises(self) -> None:
        deck = generate_deck()
        with pytest.raises(ValueError, match="78"):
            validate_deck(deck[:-1])

    def test_duplicate_raises(self) -> None:
        deck = list(generate_deck())
        deck[0] = deck[1]  # introduce a duplicate
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            validate_deck(tuple(deck))

    def test_unknown_card_raises(self) -> None:
        """Replacing a valid card with an invalid trump value should be caught."""
        deck = list(generate_deck())
        # Manually construct an out-of-range card by bypassing the factory
        from dataclasses import replace
        bad_card = Card(trump_value=99, suit=None, rank=None, is_excuse=False)
        deck[0] = bad_card
        with pytest.raises(ValueError, match="[Uu]nknown"):
            validate_deck(tuple(deck))

    def test_missing_card_raises(self) -> None:
        """Adding an extra copy of a card instead of a unique one leaves one missing."""
        deck = list(generate_deck())
        deck[-1] = deck[0]  # replace last with duplicate of first
        with pytest.raises(ValueError):
            validate_deck(tuple(deck))
