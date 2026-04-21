"""Observation models emitted from turn-by-turn play events."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.trick import CompletedTrick


@dataclass(frozen=True)
class CardPlayedObservation:
    """Observation emitted after a single card is played."""

    action: PlayAction
    trick_number: int

    def __post_init__(self) -> None:
        if self.trick_number < 1:
            raise ValueError(f"trick_number must be >= 1, got {self.trick_number}.")


@dataclass(frozen=True)
class TrickCompletedObservation:
    """Observation emitted when a trick is completed and resolved."""

    trick: CompletedTrick
