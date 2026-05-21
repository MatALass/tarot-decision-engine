"""Reusable test fixtures: pre-built hands for use across test modules.

These are built programmatically from the canonical deck, not hardcoded,
so they remain valid if card representations change.
"""

from __future__ import annotations

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.domain.hand import Dog, Hand


def _deck() -> tuple[Card, ...]:
    return generate_deck()


def strong_taker_hand() -> Hand:
    """A hand with 3 bouts, 8 trumps — typical garde candidate."""
    deck = _deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    other_trumps = [c for c in deck if c.is_trump and c.trump_value not in {1, 21}][:5]
    kings = [Card.suited(s, Rank.ROI) for s in list(Suit)[:4]]
    fillers = [c for c in deck if not c.is_trump and not c.is_excuse and c.rank != Rank.ROI][:3]
    return Hand.from_cards(bouts + other_trumps + kings + fillers)


def weak_hand() -> Hand:
    """A hand with 0 bouts, 2 trumps — typically would pass."""
    deck = _deck()
    trumps = [c for c in deck if c.is_trump and c.trump_value not in {1, 21}][:2]
    suited = [c for c in deck if c.suit is not None and c.rank not in {Rank.ROI, Rank.DAME}][:13]
    return Hand.from_cards(trumps + suited)


def average_hand() -> Hand:
    """A hand with 1 bout, 5 trumps — borderline prise."""
    deck = _deck()
    bouts = [Card.trump(21)]
    other_trumps = [c for c in deck if c.is_trump and c.trump_value != 21][:4]
    suited = [c for c in deck if c.suit is not None][:10]
    return Hand.from_cards(bouts + other_trumps + suited)


def sample_dog() -> Dog:
    """A typical dog with 3 low-value cards."""
    return Dog.from_cards([
        Card.trump(2),
        Card.suited(Suit.CLUBS, Rank.TWO),
        Card.suited(Suit.DIAMONDS, Rank.THREE),
    ])
