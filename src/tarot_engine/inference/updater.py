"""Belief-state update helpers.

The first inference version deliberately recomputes the belief state from the
latest observable GameState. This keeps the updater pure and robust while the
constraint set is still small.
"""

from __future__ import annotations

from tarot_engine.domain.game_state import GameState
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.inference.belief_state import BeliefState, build_belief_state

Observation = CardPlayedObservation | TrickCompletedObservation



def update_belief_state(
    previous_belief_state: BeliefState,
    game_state: GameState,
    observations: tuple[Observation, ...] = (),
) -> BeliefState:
    """Return the updated BeliefState for the latest observable GameState.

    ``observations`` is accepted for API stability, but the current version
    derives all hard constraints directly from ``game_state``.
    """
    if previous_belief_state.observed_player_index != game_state.context.player_index:
        raise ValueError(
            "previous_belief_state and game_state must refer to the same observed player."
        )
    return build_belief_state(game_state)
