"""Action models for turn-by-turn Tarot play."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import N_PLAYERS


@dataclass(frozen=True)
class PlayAction:
    """Atomic action: one player plays one card."""

    player_index: int
    card: Card

    def __post_init__(self) -> None:
        if not (0 <= self.player_index < N_PLAYERS):
            raise ValueError(
                f"player_index must be in [0, {N_PLAYERS - 1}], got {self.player_index}."
            )
