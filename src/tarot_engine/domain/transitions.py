"""Pure state-transition functions for turn-by-turn Tarot play."""

from __future__ import annotations

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.game_state import GameState, WorldState
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.domain.rules import Trick, TrickCard, legal_cards, trick_winner
from tarot_engine.domain.trick import CompletedTrick, TrickHistory


Observation = CardPlayedObservation | TrickCompletedObservation


def apply_play_action(state: GameState, action: PlayAction) -> tuple[GameState, tuple[Observation, ...]]:
    """Apply one played card to an observable GameState.

    Rules enforced:
    - acting player must be ``state.next_player_index``
    - if the observed player acts, the card must belong to ``remaining_hand``
    - if the observed player acts, the card must be legal according to current trick rules
    - current trick is extended, and if it reaches 5 cards it is resolved into CompletedTrick
    - next player advances in turn order, or becomes the trick winner after completion
    """
    if action.player_index != state.next_player_index:
        raise ValueError(
            f"Action player_index {action.player_index} does not match next_player_index {state.next_player_index}."
        )

    if action.player_index == state.context.player_index:
        if action.card not in state.remaining_hand:
            raise ValueError("Observed player cannot play a card that is not in remaining_hand.")
        legal = legal_cards(state.remaining_hand, Trick(state.current_trick))
        if action.card not in legal:
            raise ValueError("Observed player cannot play an illegal card in the current trick.")
        remaining_hand = tuple(card for card in state.remaining_hand if card != action.card)
    else:
        remaining_hand = state.remaining_hand

    next_trick_cards = state.current_trick + (TrickCard(card=action.card, player_index=action.player_index),)
    observations: list[Observation] = [
        CardPlayedObservation(action=action, trick_number=len(state.completed_tricks) + 1)
    ]

    if len(next_trick_cards) < 5:
        next_state = GameState(
            context=state.context,
            remaining_hand=remaining_hand,
            current_trick=next_trick_cards,
            completed_tricks=state.completed_tricks,
            next_player_index=(action.player_index + 1) % 5,
        )
        return next_state, tuple(observations)

    resolved_trick = Trick(next_trick_cards)
    completed_trick = CompletedTrick(
        cards=next_trick_cards,
        winner_index=trick_winner(resolved_trick),
        lead_player_index=next_trick_cards[0].player_index,
        trick_number=len(state.completed_tricks) + 1,
    )
    history = TrickHistory(tricks=state.completed_tricks.tricks + (completed_trick,))
    observations.append(TrickCompletedObservation(trick=completed_trick))

    next_state = GameState(
        context=state.context,
        remaining_hand=remaining_hand,
        current_trick=(),
        completed_tricks=history,
        next_player_index=completed_trick.winner_index,
    )
    return next_state, tuple(observations)



def apply_play_action_world(
    state: WorldState, action: PlayAction
) -> tuple[WorldState, tuple[Observation, ...]]:
    """Apply one played card to a complete WorldState.

    This is the fully informed counterpart of :func:`apply_play_action`.
    It additionally verifies ownership and legality against the acting player's
    real remaining hand.
    """
    if action.player_index != state.game_state.next_player_index:
        raise ValueError(
            f"Action player_index {action.player_index} does not match next_player_index {state.game_state.next_player_index}."
        )

    acting_hand = state.remaining_hands_by_player[action.player_index]
    if action.card not in acting_hand:
        raise ValueError("Player cannot play a card that is not in their remaining hand.")

    legal = legal_cards(acting_hand, Trick(state.game_state.current_trick))
    if action.card not in legal:
        raise ValueError("Player cannot play an illegal card in the current trick.")

    next_hands = list(state.remaining_hands_by_player)
    next_hands[action.player_index] = tuple(card for card in acting_hand if card != action.card)

    next_game_state, observations = apply_play_action(state.game_state, action)
    next_world_state = WorldState(
        game_state=next_game_state,
        remaining_hands_by_player=tuple(next_hands),
        dog=state.dog,
    )
    return next_world_state, observations
