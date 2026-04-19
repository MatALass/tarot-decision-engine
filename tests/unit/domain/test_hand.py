"""Tests for the Hand and Dog models."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck, HAND_SIZE, DOG_SIZE
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.domain.hand import Dog, Hand


def _make_hand(n: int = HAND_SIZE) -> list[Card]:
    """Take the first n cards from the canonical deck."""
    return list(generate_deck()[:n])


def _make_full_hand() -> Hand:
    return Hand.from_cards(_make_hand(HAND_SIZE))


class TestHandConstruction:
    def test_valid_hand_constructs(self) -> None:
        hand = _make_full_hand()
        assert len(hand) == HAND_SIZE

    def test_wrong_size_raises(self) -> None:
        with pytest.raises(ValueError, match=str(HAND_SIZE)):
            Hand.from_cards(_make_hand(14))

    def test_too_many_cards_raises(self) -> None:
        with pytest.raises(ValueError, match=str(HAND_SIZE)):
            Hand.from_cards(_make_hand(16))

    def test_duplicate_cards_raises(self) -> None:
        cards = _make_hand(14)
        cards.append(cards[0])  # duplicate
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            Hand.from_cards(cards)

    def test_hand_is_frozen(self) -> None:
        hand = _make_full_hand()
        with pytest.raises((AttributeError, TypeError)):
            hand.cards = frozenset()  # type: ignore[misc]


class TestHandStats:
    def test_hand_with_excuse_reports_has_excuse(self) -> None:
        # Excuse is first in the canonical deck
        cards = list(generate_deck()[:HAND_SIZE])
        assert cards[0].is_excuse  # verify fixture assumption
        hand = Hand.from_cards(cards)
        assert hand.has_excuse is True
        assert hand.excuse is not None
        assert hand.excuse.is_excuse

    def test_hand_without_excuse_reports_no_excuse(self) -> None:
        # Skip the first card (Excuse) and take the next 15
        cards = list(generate_deck()[1: HAND_SIZE + 1])
        hand = Hand.from_cards(cards)
        assert hand.has_excuse is False
        assert hand.excuse is None

    def test_bout_count(self) -> None:
        # Canonical deck: index 0 = Excuse, index 1 = T1, index 21 = T21 (0-indexed)
        deck = generate_deck()
        # Pick Excuse (0), T1 (1), T21 (21), and 12 non-bout suited cards
        bouts = [deck[0], deck[1], deck[21]]
        fillers = [c for c in deck if not c.is_bout][:12]
        hand = Hand.from_cards(bouts + fillers)
        assert hand.bout_count == 3

    def test_trump_count(self) -> None:
        deck = generate_deck()
        trumps = [c for c in deck if c.is_trump][:5]
        fillers = [c for c in deck if not c.is_trump and not c.is_excuse][:10]
        hand = Hand.from_cards(trumps + fillers)
        assert hand.trump_count == 5

    def test_has_petit(self) -> None:
        deck = generate_deck()
        petit = Card.trump(1)
        assert petit in deck
        fillers = [c for c in deck if c != petit and not c.is_excuse][:14]
        hand = Hand.from_cards([petit] + fillers)
        assert hand.has_petit is True

    def test_king_count(self) -> None:
        kings = [Card.suited(s, Rank.ROI) for s in Suit]  # 4 kings
        deck = generate_deck()
        fillers = [c for c in deck if c.rank != Rank.ROI and not c.is_trump and not c.is_excuse][:11]
        hand = Hand.from_cards(kings + fillers)
        assert hand.king_count == 4

    def test_point_total_is_positive(self) -> None:
        hand = _make_full_hand()
        assert hand.point_total > 0

    def test_contains_operator(self) -> None:
        deck = generate_deck()
        hand = Hand.from_cards(list(deck[:HAND_SIZE]))
        assert deck[0] in hand
        # A card not in the hand should not be found
        assert deck[HAND_SIZE] not in hand

    def test_void_suit_detected(self) -> None:
        deck = generate_deck()
        # Build a hand of all trumps (21) + Excuse — no suited cards → void in all suits
        excuse = [c for c in deck if c.is_excuse]
        trumps = [c for c in deck if c.is_trump]
        all_trumps_hand = excuse + trumps[:14]  # 1 + 14 = 15
        hand = Hand.from_cards(all_trumps_hand)
        assert hand.has_void_suit is True

    def test_no_void_suit(self) -> None:
        deck = generate_deck()
        # Carefully pick at least one card per suit
        one_per_suit = [Card.suited(s, Rank.AS) for s in Suit]  # 4 cards
        fillers = [c for c in deck if c.suit is None][:11]  # 11 trumps/excuse
        hand = Hand.from_cards(one_per_suit + fillers)
        assert hand.has_void_suit is False


class TestDog:
    def test_valid_dog_constructs(self) -> None:
        deck = generate_deck()
        dog = Dog.from_cards(list(deck[:DOG_SIZE]))
        assert len(dog) == DOG_SIZE

    def test_wrong_size_raises(self) -> None:
        deck = generate_deck()
        with pytest.raises(ValueError, match=str(DOG_SIZE)):
            Dog.from_cards(list(deck[:2]))

    def test_duplicate_in_dog_raises(self) -> None:
        deck = generate_deck()
        cards = list(deck[:2]) + [deck[0]]  # duplicate
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            Dog.from_cards(cards)

    def test_dog_point_total(self) -> None:
        dog = Dog.from_cards([Card.trump(21), Card.suited(Suit.HEARTS, Rank.ROI), Card.trump(5)])
        # T21 = 4.5, KH = 4.5, T5 = 0.5 → 9.5
        assert dog.point_total == pytest.approx(9.5)
