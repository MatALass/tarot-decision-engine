"""Projection helpers between complete and observable turn-by-turn states."""

from __future__ import annotations

from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand


def build_game_state(world_state: WorldState, player_index: int) -> GameState:
    """Project a complete WorldState into one player's observable GameState.

    The observable player sees:
    - their own remaining hand
    - the shared current trick
    - the shared completed-trick history
    - the next player to act

    Their reconstructed ``initial_hand`` is derived from:
    - their current remaining cards
    - every card they have already played in completed and current tricks
    """
    if not (0 <= player_index < len(world_state.remaining_hands_by_player)):
        raise ValueError(f"player_index out of range: {player_index}.")

    base_context = world_state.game_state.context
    reconstructed_initial_hand = Hand.from_cards(
        list(_reconstruct_initial_hand_cards(world_state, player_index))
    )
    context = InitialDealContext(
        player_index=player_index,
        taker_index=base_context.taker_index,
        contract=base_context.contract,
        initial_hand=reconstructed_initial_hand,
        partner_index=base_context.partner_index,
    )
    return GameState(
        context=context,
        remaining_hand=world_state.remaining_hands_by_player[player_index],
        current_trick=world_state.game_state.current_trick,
        completed_tricks=world_state.game_state.completed_tricks,
        next_player_index=world_state.game_state.next_player_index,
    )



def build_all_game_states(world_state: WorldState) -> tuple[GameState, ...]:
    """Project a WorldState into one observable GameState per player."""
    return tuple(build_game_state(world_state, player_index) for player_index in range(len(world_state.remaining_hands_by_player)))



def _reconstruct_initial_hand_cards(world_state: WorldState, player_index: int) -> tuple:
    remaining = tuple(world_state.remaining_hands_by_player[player_index])
    completed_played = tuple(
        trick_card.card
        for trick in world_state.game_state.completed_tricks.tricks
        for trick_card in trick.cards
        if trick_card.player_index == player_index
    )
    current_played = tuple(
        trick_card.card
        for trick_card in world_state.game_state.current_trick
        if trick_card.player_index == player_index
    )
    return remaining + completed_played + current_played
