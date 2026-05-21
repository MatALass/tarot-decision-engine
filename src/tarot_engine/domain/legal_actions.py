"""Legal PlayAction generation for observable and complete turn-by-turn states."""

from __future__ import annotations

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.game_state import GameState, WorldState
from tarot_engine.domain.rules import Trick, legal_cards



def legal_actions(game_state: GameState) -> tuple[PlayAction, ...]:
    """Return legal actions for the observed player on their turn.

    Because ``GameState`` hides other players' hands, this function is only
    defined when the observed player is the next player to act.
    """
    player_index = game_state.context.player_index
    if game_state.next_player_index != player_index:
        raise ValueError(
            "legal_actions(GameState) is only defined when the observed player is next to act."
        )
    legal = legal_cards(game_state.remaining_hand, Trick(game_state.current_trick))
    return tuple(PlayAction(player_index=player_index, card=card) for card in legal)



def legal_actions_world(world_state: WorldState) -> tuple[PlayAction, ...]:
    """Return legal actions for the actual next player in a complete WorldState."""
    player_index = world_state.game_state.next_player_index
    hand = world_state.remaining_hands_by_player[player_index]
    legal = legal_cards(hand, Trick(world_state.game_state.current_trick))
    return tuple(PlayAction(player_index=player_index, card=card) for card in legal)
