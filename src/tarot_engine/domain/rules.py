"""Tarot game rules: card legality and trick resolution.

Responsibilities (MVP scope):
- Model the lead of a trick explicitly (suit lead vs trump lead).
- Determine which cards a player may legally play.
- Determine which player wins a completed trick.

=============================================================================
CONVENTIONS
=============================================================================

TRICK LEAD
----------
  - SuitLead(suit):  First non-Excuse card was a suited card.
  - TrumpLead:       First non-Excuse card was a trump.
  - None:            No non-Excuse card played yet; next player leads freely.

The Excuse never establishes a lead.

TRICK WINNING
-------------
Priority:
  1. Highest trump (if any trump was played).
  2. Highest card of the led suit (SuitLead, no trump played).

The Excuse NEVER wins a trick.

LEGALITY
--------
SuitLead: follow suit → trump (with overcut) → défausse.
TrumpLead: trump (with overcut) → défausse.
Excuse is always legal and does not discharge the obligation.

KNOWN SIMPLIFICATION (MVP)
---------------------------
Partner-protection rule not implemented. `partner_player_index` in
`legal_cards()` is reserved for a future revision.
=============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Suit


# ---------------------------------------------------------------------------
# Lead modelling
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SuitLead:
    """The trick was led with a suited (non-trump, non-Excuse) card."""
    suit: Suit


@dataclass(frozen=True)
class TrumpLead:
    """The trick was led with a trump card."""


TrickLead = Union[SuitLead, TrumpLead, None]


def _effective_lead(cards_played: tuple["TrickCard", ...]) -> TrickLead:
    """Derive the effective lead, skipping the Excuse."""
    for tc in cards_played:
        if tc.card.is_excuse:
            continue
        if tc.card.is_trump:
            return TrumpLead()
        assert tc.card.suit is not None
        return SuitLead(suit=tc.card.suit)
    return None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TrickCard:
    """A card as played in a trick, paired with the player who played it."""
    card: Card
    player_index: int


@dataclass(frozen=True)
class Trick:
    """A completed or in-progress trick (cards in play order)."""
    cards_played: tuple[TrickCard, ...]

    def __len__(self) -> int:
        return len(self.cards_played)

    def __bool__(self) -> bool:
        return len(self.cards_played) > 0

    @property
    def is_empty(self) -> bool:
        return len(self.cards_played) == 0

    @property
    def lead(self) -> TrickLead:
        return _effective_lead(self.cards_played)

    @property
    def highest_trump(self) -> Card | None:
        trumps = [tc.card for tc in self.cards_played if tc.card.is_trump]
        return max(trumps, key=lambda c: c.trump_value) if trumps else None

    @property
    def current_winner(self) -> TrickCard | None:
        """The TrickCard currently winning, or None if empty."""
        if self.is_empty:
            return None
        candidates = [tc for tc in self.cards_played if not tc.card.is_excuse]
        if not candidates:
            return self.cards_played[0]
        trump_candidates = [tc for tc in candidates if tc.card.is_trump]
        if trump_candidates:
            return max(trump_candidates, key=lambda tc: tc.card.trump_value)
        lead = self.lead
        if isinstance(lead, SuitLead):
            led = [tc for tc in candidates if tc.card.suit == lead.suit]
            if led:
                return max(led, key=lambda tc: tc.card.rank.value)  # type: ignore[union-attr]
        return candidates[0]


# ---------------------------------------------------------------------------
# Legal cards
# ---------------------------------------------------------------------------

def legal_cards(
    hand: tuple[Card, ...],
    trick: Trick,
    *,
    partner_player_index: int | None = None,
) -> tuple[Card, ...]:
    """Return the cards a player may legally play.

    Args:
        hand:                 The player's remaining cards.
        trick:                The trick in progress (empty if leading).
        partner_player_index: Reserved — not yet implemented (MVP simplification).

    Returns:
        A non-empty tuple of legal Card objects.

    Raises:
        ValueError: If hand is empty.
    """
    if not hand:
        raise ValueError("Cannot determine legal cards for an empty hand.")

    lead = trick.lead
    if lead is None:
        return tuple(hand)

    excuse_cards = [c for c in hand if c.is_excuse]
    non_excuse = [c for c in hand if not c.is_excuse]

    if isinstance(lead, SuitLead):
        return _legal_suit_lead(lead.suit, non_excuse, excuse_cards, trick)
    return _legal_trump_lead(non_excuse, excuse_cards, trick)


def _legal_suit_lead(
    led_suit: Suit,
    non_excuse: list[Card],
    excuse_cards: list[Card],
    trick: Trick,
) -> tuple[Card, ...]:
    suit_cards = [c for c in non_excuse if c.suit == led_suit]
    if suit_cards:
        return tuple(suit_cards + excuse_cards)
    trump_cards = [c for c in non_excuse if c.is_trump]
    if trump_cards:
        return tuple(_apply_overcut(trump_cards, trick) + excuse_cards)
    if non_excuse:
        return tuple(non_excuse + excuse_cards)
    return tuple(excuse_cards)


def _legal_trump_lead(
    non_excuse: list[Card],
    excuse_cards: list[Card],
    trick: Trick,
) -> tuple[Card, ...]:
    trump_cards = [c for c in non_excuse if c.is_trump]
    if trump_cards:
        return tuple(_apply_overcut(trump_cards, trick) + excuse_cards)
    if non_excuse:
        return tuple(non_excuse + excuse_cards)
    return tuple(excuse_cards)


def _apply_overcut(trump_cards: list[Card], trick: Trick) -> list[Card]:
    """Apply overcut obligation: must play higher trump if possible."""
    highest = trick.highest_trump
    if highest is None:
        return trump_cards
    higher = [c for c in trump_cards if c.trump_value > highest.trump_value]
    return higher if higher else trump_cards


# ---------------------------------------------------------------------------
# Trick resolution
# ---------------------------------------------------------------------------

def trick_winner(trick: Trick) -> int:
    """Return the player_index of the trick winner.

    Raises:
        ValueError: If the trick is empty.
    """
    if trick.is_empty:
        raise ValueError("Cannot determine winner of an empty trick.")
    winner = trick.current_winner
    if winner is None:
        return trick.cards_played[0].player_index
    return winner.player_index
