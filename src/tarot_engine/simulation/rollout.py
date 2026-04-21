"""Roll out complete worlds from an intermediate turn-by-turn state."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.game_state import WorldState
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.domain.scoring import DealResult, score_deal
from tarot_engine.domain.transitions import Observation, apply_play_action_world
from tarot_engine.simulation.turn_policies import HeuristicTurnPolicy, TurnPolicy


@dataclass(frozen=True)
class RolloutResult:
    """Outcome of rolling a complete world to terminal state."""

    final_world_state: WorldState
    observations: tuple[Observation, ...]
    winner_piles_by_player: tuple[tuple[Card, ...], ...]
    score: DealResult


def rollout_world(
    world_state: WorldState,
    *,
    policies_by_player: tuple[TurnPolicy, ...] | None = None,
) -> RolloutResult:
    """Play a complete WorldState to the end using turn policies."""
    n_players = len(world_state.remaining_hands_by_player)
    if policies_by_player is None:
        policies_by_player = tuple(HeuristicTurnPolicy() for _ in range(n_players))
    if len(policies_by_player) != n_players:
        raise ValueError(
            f"policies_by_player must contain exactly {n_players} policies, got {len(policies_by_player)}."
        )

    current_world = world_state
    winner_piles = _winner_piles_from_world_state(world_state)
    observations: list[Observation] = []

    while not _is_terminal_world_state(current_world):
        acting_player = current_world.game_state.next_player_index
        projected_state = current_world.game_state
        if projected_state.context.player_index != acting_player:
            from tarot_engine.domain.projections import build_game_state

            projected_state = build_game_state(current_world, acting_player)
        action = policies_by_player[acting_player].select_action(projected_state)
        current_world, step_observations = apply_play_action_world(current_world, action)
        observations.extend(step_observations)
        _update_winner_piles_from_observations(winner_piles, step_observations)

    score = _score_world_state(current_world, winner_piles)
    return RolloutResult(
        final_world_state=current_world,
        observations=tuple(observations),
        winner_piles_by_player=tuple(tuple(pile) for pile in winner_piles),
        score=score,
    )



def _winner_piles_from_world_state(world_state: WorldState) -> list[list[Card]]:
    piles = [[] for _ in range(len(world_state.remaining_hands_by_player))]
    for completed_trick in world_state.game_state.completed_tricks.tricks:
        piles[completed_trick.winner_index].extend(completed_trick.played_cards)
    return piles



def _update_winner_piles_from_observations(
    winner_piles: list[list[Card]], observations: tuple[Observation, ...]
) -> None:
    for observation in observations:
        if isinstance(observation, CardPlayedObservation):
            continue
        if isinstance(observation, TrickCompletedObservation):
            winner_piles[observation.trick.winner_index].extend(observation.trick.played_cards)
            continue
        raise TypeError(f"Unsupported observation type: {type(observation)!r}")



def _score_world_state(world_state: WorldState, winner_piles: list[list[Card]]) -> DealResult:
    context = world_state.game_state.context
    taker_camp = _taker_camp(context.taker_index, context.partner_index)
    taker_pile = [card for player_index in taker_camp for card in winner_piles[player_index]]
    if context.contract.dog_counts_for_taker():
        taker_pile.extend(world_state.dog)
    taker_points = sum(card.point_value for card in taker_pile)
    bout_count = sum(1 for card in taker_pile if card.is_bout)
    return score_deal(taker_points, bout_count, context.contract)



def _taker_camp(taker_index: int, partner_index: int | None) -> frozenset[int]:
    if partner_index is None:
        return frozenset({taker_index})
    return frozenset({taker_index, partner_index})



def _is_terminal_world_state(world_state: WorldState) -> bool:
    return (
        not world_state.game_state.current_trick
        and all(len(hand) == 0 for hand in world_state.remaining_hands_by_player)
    )
