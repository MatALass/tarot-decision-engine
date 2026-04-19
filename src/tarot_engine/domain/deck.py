"""Deck generation and validation for a standard 78-card Tarot deck.

Responsibilities:
- Generate the canonical 78-card deck deterministically.
- Validate that an arbitrary collection of cards constitutes a valid deck.

This module has no knowledge of simulation, scoring, or hands.
"""

from __future__ import annotations

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Rank, Suit

# A standard 5-player Tarot deal: 15 cards per player, 3 in the dog.
DECK_SIZE = 78
HAND_SIZE = 15
DOG_SIZE = 3
N_PLAYERS = 5

# Sanity check: 5 × 15 + 3 = 78.
assert N_PLAYERS * HAND_SIZE + DOG_SIZE == DECK_SIZE


def generate_deck() -> tuple[Card, ...]:
    """Return the canonical 78-card Tarot deck as an immutable tuple.

    Order: Excuse, trumps 1–21, then suited cards (Spades, Hearts, Diamonds, Clubs)
    each from AS to ROI. Order is deterministic and irrelevant to correctness
    (the deck is shuffled externally), but consistency aids testing.
    """
    cards: list[Card] = []

    # The Excuse
    cards.append(Card.excuse())

    # 21 numbered trumps
    for value in range(1, 22):
        cards.append(Card.trump(value))

    # 4 suits × 14 ranks = 56 suited cards
    for suit in Suit:
        for rank in Rank:
            cards.append(Card.suited(suit, rank))

    deck = tuple(cards)
    # Internal consistency check — should never fail if the above logic is correct.
    _assert_deck_invariants(deck)
    return deck


def validate_deck(cards: tuple[Card, ...]) -> None:
    """Validate that a collection of cards is a well-formed 78-card Tarot deck.

    Args:
        cards: The collection to validate.

    Raises:
        ValueError: With a descriptive message for each violation found.
    """
    errors: list[str] = []

    # 1. Size
    if len(cards) != DECK_SIZE:
        errors.append(f"Deck must contain exactly {DECK_SIZE} cards, got {len(cards)}.")

    # 2. Uniqueness
    seen: set[Card] = set()
    duplicates: set[Card] = set()
    for card in cards:
        if card in seen:
            duplicates.add(card)
        seen.add(card)
    if duplicates:
        dup_strs = ", ".join(str(c) for c in sorted(duplicates, key=str))
        errors.append(f"Duplicate cards found: {dup_strs}.")

    # 3. Composition against the canonical deck
    canonical = set(generate_deck())
    unknown = seen - canonical
    if unknown:
        unk_strs = ", ".join(str(c) for c in sorted(unknown, key=str))
        errors.append(f"Unknown cards not part of a standard deck: {unk_strs}.")

    missing = canonical - seen
    if missing:
        mis_strs = ", ".join(str(c) for c in sorted(missing, key=str))
        errors.append(f"Missing cards from standard deck: {mis_strs}.")

    if errors:
        raise ValueError("Invalid deck:\n" + "\n".join(f"  - {e}" for e in errors))


def _assert_deck_invariants(deck: tuple[Card, ...]) -> None:
    """Internal sanity check on a generated deck. Raises AssertionError on failure."""
    assert len(deck) == DECK_SIZE, f"Expected {DECK_SIZE} cards, got {len(deck)}"
    assert len(set(deck)) == DECK_SIZE, "Generated deck contains duplicates"

    excuse_count = sum(1 for c in deck if c.is_excuse)
    assert excuse_count == 1, f"Expected 1 Excuse, got {excuse_count}"

    trump_count = sum(1 for c in deck if c.is_trump)
    assert trump_count == 21, f"Expected 21 trumps, got {trump_count}"

    suited_count = sum(1 for c in deck if c.suit is not None)
    assert suited_count == 56, f"Expected 56 suited cards, got {suited_count}"
