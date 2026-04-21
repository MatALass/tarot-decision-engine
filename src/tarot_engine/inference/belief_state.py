"""Belief-state model for hidden-card inference."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import DOG_SIZE, N_PLAYERS, generate_deck
from tarot_engine.domain.game_state import GameState
from tarot_engine.inference.constraints import HardConstraints, derive_hard_constraints


@dataclass(frozen=True)
class BeliefState:
    """Minimal hidden-state belief model based on hard constraints only."""

    observed_player_index: int
    known_remaining_hand: tuple[Card, ...]
    played_cards: tuple[Card, ...]
    remaining_card_counts_by_player: tuple[int, ...]
    impossible_cards_by_player: tuple[frozenset[Card], ...]
    dog_impossible_cards: frozenset[Card]
    dog_card_count: int = DOG_SIZE

    def __post_init__(self) -> None:
        if not (0 <= self.observed_player_index < N_PLAYERS):
            raise ValueError(
                f"observed_player_index must be in [0, {N_PLAYERS - 1}], got {self.observed_player_index}."
            )
        if len(self.remaining_card_counts_by_player) != N_PLAYERS:
            raise ValueError(
                f"remaining_card_counts_by_player must contain exactly {N_PLAYERS} entries, got {len(self.remaining_card_counts_by_player)}."
            )
        if len(self.impossible_cards_by_player) != N_PLAYERS:
            raise ValueError(
                f"impossible_cards_by_player must contain exactly {N_PLAYERS} entries, got {len(self.impossible_cards_by_player)}."
            )
        if self.dog_card_count < 0:
            raise ValueError(f"dog_card_count must be >= 0, got {self.dog_card_count}.")
        if len(set(self.known_remaining_hand)) != len(self.known_remaining_hand):
            raise ValueError("known_remaining_hand cannot contain duplicate cards.")
        if len(set(self.played_cards)) != len(self.played_cards):
            raise ValueError("played_cards cannot contain duplicate cards.")
        if set(self.known_remaining_hand) & set(self.played_cards):
            raise ValueError("known_remaining_hand and played_cards must be disjoint.")
        if self.remaining_card_counts_by_player[self.observed_player_index] != len(self.known_remaining_hand):
            raise ValueError(
                "remaining_card_counts_by_player is inconsistent with known_remaining_hand for the observed player."
            )
        accounted_cards = (
            sum(self.remaining_card_counts_by_player)
            + self.dog_card_count
            + len(self.played_cards)
        )
        if accounted_cards != len(generate_deck()):
            raise ValueError(
                f"BeliefState must account for exactly {len(generate_deck())} cards, got {accounted_cards}."
            )

    @property
    def known_cards(self) -> frozenset[Card]:
        return frozenset(self.known_remaining_hand) | frozenset(self.played_cards)

    @property
    def unknown_cards(self) -> tuple[Card, ...]:
        return tuple(card for card in generate_deck() if card not in self.known_cards)

    def possible_cards_for_player(self, player_index: int) -> tuple[Card, ...]:
        if player_index == self.observed_player_index:
            return self.known_remaining_hand
        impossible = self.impossible_cards_by_player[player_index]
        return tuple(card for card in self.unknown_cards if card not in impossible)

    def possible_dog_cards(self) -> tuple[Card, ...]:
        return tuple(card for card in self.unknown_cards if card not in self.dog_impossible_cards)



def build_belief_state(game_state: GameState) -> BeliefState:
    """Build a minimal BeliefState directly from a GameState."""
    constraints = derive_hard_constraints(game_state)
    remaining_card_counts = _remaining_card_counts_by_player(game_state)
    return BeliefState(
        observed_player_index=game_state.context.player_index,
        known_remaining_hand=tuple(game_state.remaining_hand),
        played_cards=tuple(game_state.played_cards),
        remaining_card_counts_by_player=remaining_card_counts,
        impossible_cards_by_player=constraints.impossible_cards_by_player,
        dog_impossible_cards=constraints.dog_impossible_cards,
    )



def build_belief_state_from_constraints(
    game_state: GameState, constraints: HardConstraints
) -> BeliefState:
    """Build a BeliefState from a GameState and precomputed HardConstraints."""
    return BeliefState(
        observed_player_index=game_state.context.player_index,
        known_remaining_hand=tuple(game_state.remaining_hand),
        played_cards=tuple(game_state.played_cards),
        remaining_card_counts_by_player=_remaining_card_counts_by_player(game_state),
        impossible_cards_by_player=constraints.impossible_cards_by_player,
        dog_impossible_cards=constraints.dog_impossible_cards,
    )



def _remaining_card_counts_by_player(game_state: GameState) -> tuple[int, ...]:
    counts_played = [0 for _ in range(N_PLAYERS)]
    for trick in game_state.completed_tricks.tricks:
        for trick_card in trick.cards:
            counts_played[trick_card.player_index] += 1
    for trick_card in game_state.current_trick:
        counts_played[trick_card.player_index] += 1

    remaining = [15 - played for played in counts_played]
    observed_player = game_state.context.player_index
    remaining[observed_player] = len(game_state.remaining_hand)
    return tuple(remaining)
