"""Core state models for future turn-by-turn Tarot decision-making."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import DECK_SIZE, N_PLAYERS
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import TrickHistory


@dataclass(frozen=True)
class InitialDealContext:
    """Immutable initial context for one player's decision process."""

    player_index: int
    taker_index: int
    contract: Contract
    initial_hand: Hand
    partner_index: int | None = None

    def __post_init__(self) -> None:
        if not (0 <= self.player_index < N_PLAYERS):
            raise ValueError(
                f"player_index must be in [0, {N_PLAYERS - 1}], got {self.player_index}."
            )
        if not (0 <= self.taker_index < N_PLAYERS):
            raise ValueError(
                f"taker_index must be in [0, {N_PLAYERS - 1}], got {self.taker_index}."
            )
        if self.partner_index is not None:
            if not (0 <= self.partner_index < N_PLAYERS):
                raise ValueError(
                    f"partner_index must be in [0, {N_PLAYERS - 1}], got {self.partner_index}."
                )
            if self.partner_index == self.taker_index:
                raise ValueError("partner_index cannot be equal to taker_index.")


@dataclass(frozen=True)
class GameState:
    """Observable current state from one player's perspective.

    Important design constraint:
    ``remaining_hand`` is a dynamic tuple of cards and intentionally does NOT use
    ``Hand``, which remains reserved for the initial 15-card deal only.
    """

    context: InitialDealContext
    remaining_hand: tuple[Card, ...]
    current_trick: tuple[TrickCard, ...]
    completed_tricks: TrickHistory
    next_player_index: int

    def __post_init__(self) -> None:
        if len(set(self.remaining_hand)) != len(self.remaining_hand):
            raise ValueError("remaining_hand cannot contain duplicate cards.")
        if not set(self.remaining_hand).issubset(self.context.initial_hand.cards):
            raise ValueError("remaining_hand must be a subset of the initial_hand.")

        if not (0 <= len(self.current_trick) <= N_PLAYERS - 1):
            raise ValueError(
                f"current_trick size must be in [0, {N_PLAYERS - 1}], got {len(self.current_trick)}."
            )
        if not (0 <= self.next_player_index < N_PLAYERS):
            raise ValueError(
                f"next_player_index must be in [0, {N_PLAYERS - 1}], got {self.next_player_index}."
            )

        current_players = [trick_card.player_index for trick_card in self.current_trick]
        if len(set(current_players)) != len(current_players):
            raise ValueError("current_trick cannot contain duplicate player indices.")
        if self.next_player_index in current_players:
            raise ValueError("next_player_index cannot already have played in current_trick.")

        played_cards = set(self.played_cards)
        if played_cards & set(self.remaining_hand):
            raise ValueError("remaining_hand must not contain cards already played.")

        own_played_cards = {
            trick_card.card
            for trick_card in self.current_trick
            if trick_card.player_index == self.context.player_index
        }
        own_played_cards.update(
            trick_card.card
            for trick in self.completed_tricks.tricks
            for trick_card in trick.cards
            if trick_card.player_index == self.context.player_index
        )
        if not own_played_cards.issubset(self.context.initial_hand.cards):
            raise ValueError("Cards already played by the observed player must come from initial_hand.")

        expected_remaining = self.context.initial_hand.cards - own_played_cards
        if set(self.remaining_hand) != expected_remaining:
            raise ValueError(
                "remaining_hand is inconsistent with the observed player's initial_hand and already played cards."
            )

    @property
    def played_cards(self) -> tuple[Card, ...]:
        history_cards = self.completed_tricks.cards_played
        current_cards = tuple(trick_card.card for trick_card in self.current_trick)
        return history_cards + current_cards


@dataclass(frozen=True)
class WorldState:
    """Complete simulated state, including hidden information."""

    game_state: GameState
    remaining_hands_by_player: tuple[tuple[Card, ...], ...]
    dog: tuple[Card, ...] = ()

    def __post_init__(self) -> None:
        if len(self.remaining_hands_by_player) != N_PLAYERS:
            raise ValueError(
                f"remaining_hands_by_player must contain exactly {N_PLAYERS} hands, got {len(self.remaining_hands_by_player)}."
            )

        all_hand_cards: list[Card] = []
        for hand in self.remaining_hands_by_player:
            if len(set(hand)) != len(hand):
                raise ValueError("A player remaining hand cannot contain duplicate cards.")
            all_hand_cards.extend(hand)

        if len(set(self.dog)) != len(self.dog):
            raise ValueError("dog cannot contain duplicate cards.")

        all_zone_cards = (
            all_hand_cards
            + list(self.dog)
            + list(self.game_state.played_cards)
        )
        if len(set(all_zone_cards)) != len(all_zone_cards):
            raise ValueError("WorldState cannot contain duplicate cards across hands, dog, and tricks.")
        if len(all_zone_cards) > DECK_SIZE:
            raise ValueError(
                f"WorldState cannot contain more than {DECK_SIZE} cards, got {len(all_zone_cards)}."
            )

        observed_player_index = self.game_state.context.player_index
        observed_hand = self.remaining_hands_by_player[observed_player_index]
        if tuple(observed_hand) != self.game_state.remaining_hand:
            raise ValueError(
                "remaining_hands_by_player for the observed player must match GameState.remaining_hand."
            )
