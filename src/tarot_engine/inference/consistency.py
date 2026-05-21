"""Consistency checks between sampled worlds and belief states."""

from __future__ import annotations

from tarot_engine.domain.game_state import WorldState
from tarot_engine.domain.projections import build_game_state
from tarot_engine.inference.belief_state import BeliefState



def validate_world_against_belief_state(world_state: WorldState, belief_state: BeliefState) -> None:
    """Raise ValueError if a world is inconsistent with a BeliefState."""
    observed = belief_state.observed_player_index
    if tuple(world_state.remaining_hands_by_player[observed]) != belief_state.known_remaining_hand:
        raise ValueError("Observed player's remaining hand is inconsistent with BeliefState.")

    for player_index, hand in enumerate(world_state.remaining_hands_by_player):
        if len(hand) != belief_state.remaining_card_counts_by_player[player_index]:
            raise ValueError(
                f"Player {player_index} hand size is inconsistent with BeliefState."
            )
        impossible = belief_state.impossible_cards_by_player[player_index]
        forbidden = set(hand) & set(impossible)
        if forbidden:
            raise ValueError(
                f"Player {player_index} has cards forbidden by BeliefState: {sorted(forbidden, key=str)}."
            )

    if len(world_state.dog) != belief_state.dog_card_count:
        raise ValueError("Dog size is inconsistent with BeliefState.")
    dog_forbidden = set(world_state.dog) & set(belief_state.dog_impossible_cards)
    if dog_forbidden:
        raise ValueError(
            f"Dog contains cards forbidden by BeliefState: {sorted(dog_forbidden, key=str)}."
        )

    projected = build_game_state(world_state, observed)
    if projected != world_state.game_state:
        raise ValueError("WorldState does not reproduce the observable GameState for the observed player.")



def world_matches_belief_state(world_state: WorldState, belief_state: BeliefState) -> bool:
    """Return True if a world is consistent with a BeliefState."""
    try:
        validate_world_against_belief_state(world_state, belief_state)
    except ValueError:
        return False
    return True
