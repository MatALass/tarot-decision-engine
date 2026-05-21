"""Card model for the Tarot domain.

A Card is an immutable value object. All properties are either stored directly
or derived deterministically from stored fields — no external state, no mutation.

Design notes:
- trump_value is only meaningful for trump cards (is_trump == True).
  For suited cards it is 0. This avoids an Optional and simplifies comparisons.
- is_excuse is a special flag: the Excuse is neither a trump in the trick-winning
  sense nor a suited card. It is tracked explicitly.
- is_bout is derived: only the Excuse, trump 1, and trump 21 are bouts.
  Not stored separately to avoid redundancy.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.enums import Rank, Suit

# Trump values range from 1 to 21.
TRUMP_MIN = 1
TRUMP_MAX = 21

# The three bouts (oudlers) by their trump values.
BOUT_TRUMP_VALUES: frozenset[int] = frozenset({1, 21})


@dataclass(frozen=True, order=False)
class Card:
    """An immutable Tarot card.

    Exactly one of the following is true for any valid Card:
    - is_excuse is True  (the unique Excuse card)
    - is_trump is True   (one of the 21 numbered trumps)
    - suit is not None   (a suited card: one of 4 suits × 14 ranks)

    These states are mutually exclusive and enforced at construction via
    the class-level factory methods.
    """

    # For trump cards: value in [1, 21]. For all others: 0.
    trump_value: int

    # For suited cards: the suit. None for trumps and the Excuse.
    suit: Suit | None

    # For suited cards: the rank. None for trumps and the Excuse.
    rank: Rank | None

    # True only for the unique Excuse card.
    is_excuse: bool

    # ---------------------------------------------------------------------------
    # Factory methods — the only legitimate way to construct Card instances.
    # ---------------------------------------------------------------------------

    @classmethod
    def trump(cls, value: int) -> Card:
        """Create a numbered trump card.

        Args:
            value: Trump number in [1, 21].

        Raises:
            ValueError: If the value is outside the valid trump range.
        """
        if not (TRUMP_MIN <= value <= TRUMP_MAX):
            raise ValueError(
                f"Trump value must be between {TRUMP_MIN} and {TRUMP_MAX}, got {value}."
            )
        return cls(trump_value=value, suit=None, rank=None, is_excuse=False)

    @classmethod
    def suited(cls, suit: Suit, rank: Rank) -> Card:
        """Create a suited card (non-trump, non-excuse).

        Args:
            suit: The card's suit.
            rank: The card's rank.
        """
        return cls(trump_value=0, suit=suit, rank=rank, is_excuse=False)

    @classmethod
    def excuse(cls) -> Card:
        """Create the unique Excuse card."""
        return cls(trump_value=0, suit=None, rank=None, is_excuse=True)

    # ---------------------------------------------------------------------------
    # Derived properties — no stored state, purely computed.
    # ---------------------------------------------------------------------------

    @property
    def is_trump(self) -> bool:
        """True for numbered trump cards (1–21). The Excuse is NOT a trump here."""
        return not self.is_excuse and self.trump_value > 0

    @property
    def is_bout(self) -> bool:
        """True for the three bouts (oudlers): Excuse, trump 1 (Petit), trump 21 (Monde).

        Bouts determine the required point threshold for the taker's camp.
        """
        return self.is_excuse or self.trump_value in BOUT_TRUMP_VALUES

    @property
    def point_value(self) -> float:
        """Card point value for scoring purposes.

        Bouts are worth 4.5 pts, Kings 4.5, Queens 3.5, Knights 2.5, Jacks 1.5,
        all other cards 0.5 pt. (Standard French Tarot scoring counts cards in
        pairs; the 0.5 convention handles individual card accounting cleanly.)
        """
        if self.is_excuse:
            return 4.5
        if self.is_trump:
            return 4.5 if self.trump_value in BOUT_TRUMP_VALUES else 0.5
        # Suited card
        assert self.rank is not None
        return {
            Rank.ROI: 4.5,
            Rank.DAME: 3.5,
            Rank.CAVALIER: 2.5,
            Rank.VALET: 1.5,
        }.get(self.rank, 0.5)

    # ---------------------------------------------------------------------------
    # Representation
    # ---------------------------------------------------------------------------

    def __repr__(self) -> str:
        if self.is_excuse:
            return "Card(EXCUSE)"
        if self.is_trump:
            return f"Card(T{self.trump_value})"
        return f"Card({self.rank.name}{self.suit.value})"  # type: ignore[union-attr]

    def __str__(self) -> str:
        if self.is_excuse:
            return "EXCUSE"
        if self.is_trump:
            return f"T{self.trump_value}"
        return f"{self.rank.name[0] if self.rank.name not in ('AS', 'TEN') else self.rank.name[:2]}{self.suit.value}"  # type: ignore[union-attr]
