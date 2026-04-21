"""Immutable trick-history models for turn-by-turn Tarot play."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.deck import N_PLAYERS
from tarot_engine.domain.rules import TrickCard


@dataclass(frozen=True)
class CompletedTrick:
    """A fully resolved trick kept in history.

    This is intentionally separate from ``domain.rules.Trick``:
    - ``rules.Trick`` models rule resolution for an in-progress or complete trick
    - ``CompletedTrick`` models an immutable historical fact in the game timeline
    """

    cards: tuple[TrickCard, ...]
    winner_index: int
    lead_player_index: int
    trick_number: int

    def __post_init__(self) -> None:
        if len(self.cards) != N_PLAYERS:
            raise ValueError(
                f"A completed trick must contain exactly {N_PLAYERS} cards, got {len(self.cards)}."
            )
        if not (0 <= self.winner_index < N_PLAYERS):
            raise ValueError(
                f"winner_index must be in [0, {N_PLAYERS - 1}], got {self.winner_index}."
            )
        if not (0 <= self.lead_player_index < N_PLAYERS):
            raise ValueError(
                f"lead_player_index must be in [0, {N_PLAYERS - 1}], got {self.lead_player_index}."
            )
        if self.trick_number < 1:
            raise ValueError(f"trick_number must be >= 1, got {self.trick_number}.")

        player_indices = [trick_card.player_index for trick_card in self.cards]
        if len(set(player_indices)) != len(player_indices):
            raise ValueError("A completed trick cannot contain duplicate player indices.")
        if self.cards[0].player_index != self.lead_player_index:
            raise ValueError(
                "lead_player_index must match the player_index of the first card in trick order."
            )
        if self.winner_index not in player_indices:
            raise ValueError("winner_index must belong to one of the trick's played cards.")

    @property
    def played_cards(self) -> tuple:
        return tuple(trick_card.card for trick_card in self.cards)


@dataclass(frozen=True)
class TrickHistory:
    """Ordered history of completed tricks."""

    tricks: tuple[CompletedTrick, ...]

    def __post_init__(self) -> None:
        trick_numbers = [trick.trick_number for trick in self.tricks]
        expected = list(range(1, len(self.tricks) + 1))
        if trick_numbers != expected:
            raise ValueError(
                f"TrickHistory trick numbers must be contiguous from 1. Got {trick_numbers}, expected {expected}."
            )

    def __len__(self) -> int:
        return len(self.tricks)

    @property
    def cards_played(self) -> tuple:
        return tuple(card for trick in self.tricks for card in trick.played_cards)
