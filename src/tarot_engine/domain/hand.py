"""Hand model for the Tarot domain.

A Hand is an immutable, validated collection of Card objects held by one player.
It knows nothing about parsing (that is utils/parsing.py's job) and nothing
about simulation or scoring.

Responsibilities:
- Hold a player's cards as a frozenset (order is irrelevant during play).
- Validate that the hand is correctly sized.
- Expose derived statistics useful for decision-making (trump count, bout count, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import HAND_SIZE, DOG_SIZE
from tarot_engine.domain.enums import Rank


@dataclass(frozen=True)
class Hand:
    """An immutable, validated player hand.

    Args:
        cards: The cards held by the player. Must be exactly HAND_SIZE (15).

    Raises:
        ValueError: If the hand size is incorrect or cards are not unique.
    """

    cards: frozenset[Card]

    def __post_init__(self) -> None:
        if len(self.cards) != HAND_SIZE:
            raise ValueError(
                f"A player hand must contain exactly {HAND_SIZE} cards, "
                f"got {len(self.cards)}."
            )

    # ---------------------------------------------------------------------------
    # Alternative constructors
    # ---------------------------------------------------------------------------

    @classmethod
    def from_cards(cls, cards: list[Card] | tuple[Card, ...]) -> Hand:
        """Construct a Hand from a sequence of Card objects.

        Duplicates are detected here (frozenset collapses them, size check catches it).

        Args:
            cards: Sequence of Card objects to form the hand.

        Raises:
            ValueError: If there are duplicates (size mismatch after dedup) or
                        wrong number of cards supplied.
        """
        unique = frozenset(cards)
        if len(unique) != len(cards):
            raise ValueError(
                f"Hand contains duplicate cards. "
                f"Supplied {len(cards)} cards, {len(unique)} unique."
            )
        return cls(cards=unique)

    @classmethod
    def dog(cls, cards: list[Card] | tuple[Card, ...]) -> "Dog":
        """Construct a Dog (chien) from a sequence of Card objects."""
        return Dog.from_cards(cards)

    # ---------------------------------------------------------------------------
    # Derived statistics — pure computation, no side effects
    # ---------------------------------------------------------------------------

    @property
    def trumps(self) -> frozenset[Card]:
        """All numbered trump cards in the hand (Excuse excluded)."""
        return frozenset(c for c in self.cards if c.is_trump)

    @property
    def trump_count(self) -> int:
        """Number of numbered trump cards (Excuse excluded)."""
        return len(self.trumps)

    @property
    def excuse(self) -> Card | None:
        """The Excuse card if present in the hand, else None."""
        for card in self.cards:
            if card.is_excuse:
                return card
        return None

    @property
    def has_excuse(self) -> bool:
        """True if the Excuse is in the hand."""
        return self.excuse is not None

    @property
    def bouts(self) -> frozenset[Card]:
        """All bouts (oudlers) in the hand: Excuse, Petit (T1), Monde (T21)."""
        return frozenset(c for c in self.cards if c.is_bout)

    @property
    def bout_count(self) -> int:
        """Number of bouts in the hand."""
        return len(self.bouts)

    @property
    def has_petit(self) -> bool:
        """True if trump 1 (le Petit) is in the hand."""
        return any(c.is_trump and c.trump_value == 1 for c in self.cards)

    @property
    def kings(self) -> frozenset[Card]:
        """All kings in the hand."""
        return frozenset(c for c in self.cards if c.rank == Rank.ROI)

    @property
    def king_count(self) -> int:
        """Number of kings in the hand."""
        return len(self.kings)

    @property
    def point_total(self) -> float:
        """Sum of point values of all cards in the hand."""
        return sum(c.point_value for c in self.cards)

    @property
    def has_void_suit(self) -> bool:
        """True if the hand has no cards in at least one of the four suits."""
        from tarot_engine.domain.enums import Suit
        suits_present = {c.suit for c in self.cards if c.suit is not None}
        return len(suits_present) < 4

    # ---------------------------------------------------------------------------
    # Representation
    # ---------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.cards)

    def __contains__(self, card: object) -> bool:
        return card in self.cards

    def __repr__(self) -> str:
        sorted_cards = sorted(self.cards, key=_card_sort_key)
        return f"Hand([{', '.join(str(c) for c in sorted_cards)}])"


@dataclass(frozen=True)
class Dog:
    """The dog (chien) — 3 face-down cards set aside before the deal.

    Same structure as Hand but with a different size constraint.
    Kept as a distinct type to avoid accidentally passing a Dog where a Hand
    is expected (and vice versa).
    """

    cards: frozenset[Card]

    def __post_init__(self) -> None:
        if len(self.cards) != DOG_SIZE:
            raise ValueError(
                f"The dog must contain exactly {DOG_SIZE} cards, "
                f"got {len(self.cards)}."
            )

    @classmethod
    def from_cards(cls, cards: list[Card] | tuple[Card, ...]) -> Dog:
        """Construct a Dog from a sequence of Card objects."""
        unique = frozenset(cards)
        if len(unique) != len(cards):
            raise ValueError(
                f"Dog contains duplicate cards. "
                f"Supplied {len(cards)} cards, {len(unique)} unique."
            )
        return cls(cards=unique)

    @property
    def point_total(self) -> float:
        """Sum of point values of all cards in the dog."""
        return sum(c.point_value for c in self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __contains__(self, card: object) -> bool:
        return card in self.cards

    def __repr__(self) -> str:
        sorted_cards = sorted(self.cards, key=_card_sort_key)
        return f"Dog([{', '.join(str(c) for c in sorted_cards)}])"


def _card_sort_key(card: Card) -> tuple[int, int, int]:
    """Stable sort key for display: Excuse first, then trumps desc, then suited."""
    if card.is_excuse:
        return (0, 0, 0)
    if card.is_trump:
        return (1, -card.trump_value, 0)
    # Suited: group by suit ordinal, then rank value
    suit_order = list(card.suit.__class__)
    return (2, suit_order.index(card.suit), card.rank.value)  # type: ignore[union-attr]
