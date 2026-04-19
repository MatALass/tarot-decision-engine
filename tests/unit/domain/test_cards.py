"""Tests for the Card model."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Rank, Suit


class TestCardFactories:
    def test_trump_creates_valid_trump(self) -> None:
        card = Card.trump(10)
        assert card.is_trump is True
        assert card.trump_value == 10
        assert card.suit is None
        assert card.rank is None
        assert card.is_excuse is False

    def test_trump_boundary_values(self) -> None:
        Card.trump(1)   # should not raise
        Card.trump(21)  # should not raise

    def test_trump_invalid_values(self) -> None:
        with pytest.raises(ValueError):
            Card.trump(0)
        with pytest.raises(ValueError):
            Card.trump(22)
        with pytest.raises(ValueError):
            Card.trump(-1)

    def test_suited_creates_valid_suited_card(self) -> None:
        card = Card.suited(Suit.HEARTS, Rank.ROI)
        assert card.is_trump is False
        assert card.is_excuse is False
        assert card.suit == Suit.HEARTS
        assert card.rank == Rank.ROI
        assert card.trump_value == 0

    def test_excuse_creates_valid_excuse(self) -> None:
        card = Card.excuse()
        assert card.is_excuse is True
        assert card.is_trump is False
        assert card.suit is None
        assert card.rank is None
        assert card.trump_value == 0


class TestCardImmutability:
    def test_card_is_frozen(self) -> None:
        card = Card.trump(5)
        with pytest.raises((AttributeError, TypeError)):
            card.trump_value = 99  # type: ignore[misc]

    def test_equal_cards_are_identical(self) -> None:
        a = Card.trump(21)
        b = Card.trump(21)
        assert a == b
        assert hash(a) == hash(b)

    def test_different_cards_are_not_equal(self) -> None:
        assert Card.trump(1) != Card.trump(21)
        assert Card.trump(1) != Card.suited(Suit.SPADES, Rank.AS)
        assert Card.excuse() != Card.trump(1)

    def test_cards_usable_in_set(self) -> None:
        cards = {Card.trump(1), Card.trump(1), Card.excuse()}
        assert len(cards) == 2


class TestCardProperties:
    def test_excuse_is_bout(self) -> None:
        assert Card.excuse().is_bout is True

    def test_petit_is_bout(self) -> None:
        assert Card.trump(1).is_bout is True

    def test_monde_is_bout(self) -> None:
        assert Card.trump(21).is_bout is True

    def test_non_bout_trump_is_not_bout(self) -> None:
        for value in range(2, 21):
            assert Card.trump(value).is_bout is False

    def test_suited_card_is_not_bout(self) -> None:
        assert Card.suited(Suit.HEARTS, Rank.ROI).is_bout is False

    def test_excuse_not_trump(self) -> None:
        assert Card.excuse().is_trump is False


class TestCardPointValues:
    """Point values follow standard French Tarot scoring."""

    def test_excuse_worth_four_and_half(self) -> None:
        assert Card.excuse().point_value == 4.5

    def test_petit_worth_four_and_half(self) -> None:
        assert Card.trump(1).point_value == 4.5

    def test_monde_worth_four_and_half(self) -> None:
        assert Card.trump(21).point_value == 4.5

    def test_non_bout_trump_worth_half(self) -> None:
        for value in range(2, 21):
            assert Card.trump(value).point_value == 0.5

    def test_king_worth_four_and_half(self) -> None:
        assert Card.suited(Suit.HEARTS, Rank.ROI).point_value == 4.5

    def test_queen_worth_three_and_half(self) -> None:
        assert Card.suited(Suit.HEARTS, Rank.DAME).point_value == 3.5

    def test_cavalier_worth_two_and_half(self) -> None:
        assert Card.suited(Suit.HEARTS, Rank.CAVALIER).point_value == 2.5

    def test_valet_worth_one_and_half(self) -> None:
        assert Card.suited(Suit.HEARTS, Rank.VALET).point_value == 1.5

    def test_small_cards_worth_half(self) -> None:
        for rank in [Rank.AS, Rank.TWO, Rank.THREE, Rank.TEN]:
            assert Card.suited(Suit.CLUBS, rank).point_value == 0.5

    def test_total_deck_points(self) -> None:
        """The 78-card deck has a fixed total: 91 points."""
        from tarot_engine.domain.deck import generate_deck
        total = sum(c.point_value for c in generate_deck())
        assert total == pytest.approx(91.0)
