"""Sampler for hidden worlds compatible with an observable GameState."""

from __future__ import annotations

import random
from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.game_state import GameState, WorldState
from tarot_engine.inference.belief_state import BeliefState, build_belief_state
from tarot_engine.inference.consistency import validate_world_against_belief_state
from tarot_engine.inference.likelihood import WorldLikelihood, score_world_likelihood


@dataclass(frozen=True)
class WeightedWorldSample:
    """One sampled world together with its plausibility score."""

    world_state: WorldState
    likelihood: WorldLikelihood



def sample_compatible_world(
    game_state: GameState,
    rng: random.Random,
    belief_state: BeliefState | None = None,
) -> WorldState:
    """Sample one complete WorldState compatible with the observable state.

    The sampler is now weighted by posterior marginals instead of treating all
    compatible destinations uniformly. This preserves compatibility while
    producing more plausible hidden worlds on average.
    """
    return sample_weighted_world(game_state, rng, belief_state).world_state



def sample_weighted_world(
    game_state: GameState,
    rng: random.Random,
    belief_state: BeliefState | None = None,
) -> WeightedWorldSample:
    """Sample one compatible world and return its likelihood diagnostics."""
    if belief_state is None:
        belief_state = build_belief_state(game_state)
    if belief_state.observed_player_index != game_state.context.player_index:
        raise ValueError("belief_state must target the same observed player as game_state.")

    observed = belief_state.observed_player_index
    unknown_cards = list(belief_state.unknown_cards)
    assignment = {
        ("player", observed): list(game_state.remaining_hand),
        ("dog", None): [],
    }
    slot_capacity = {
        ("player", player_index): belief_state.remaining_card_counts_by_player[player_index]
        for player_index in range(len(belief_state.remaining_card_counts_by_player))
        if player_index != observed
    }
    slot_capacity[("dog", None)] = belief_state.dog_card_count

    rng.shuffle(unknown_cards)
    posterior = belief_state.posterior
    if not _assign_unknown_cards(unknown_cards, slot_capacity, assignment, belief_state, posterior, rng):
        raise ValueError("Failed to sample a world compatible with the current BeliefState.")

    remaining_hands = []
    for player_index in range(len(belief_state.remaining_card_counts_by_player)):
        if player_index == observed:
            remaining_hands.append(tuple(game_state.remaining_hand))
        else:
            remaining_hands.append(tuple(assignment[("player", player_index)]))
    world_state = WorldState(
        game_state=game_state,
        remaining_hands_by_player=tuple(remaining_hands),
        dog=tuple(assignment[("dog", None)]),
    )
    validate_world_against_belief_state(world_state, belief_state)
    return WeightedWorldSample(
        world_state=world_state,
        likelihood=score_world_likelihood(world_state, belief_state),
    )



def sample_compatible_worlds(
    game_state: GameState,
    n_samples: int,
    rng: random.Random,
    belief_state: BeliefState | None = None,
) -> tuple[WorldState, ...]:
    """Sample multiple complete WorldState instances compatible with the observable state."""
    if n_samples < 1:
        raise ValueError(f"n_samples must be >= 1, got {n_samples}.")
    if belief_state is None:
        belief_state = build_belief_state(game_state)
    return tuple(sample_compatible_world(game_state, rng, belief_state) for _ in range(n_samples))



def sample_weighted_worlds(
    game_state: GameState,
    n_samples: int,
    rng: random.Random,
    belief_state: BeliefState | None = None,
) -> tuple[WeightedWorldSample, ...]:
    """Sample multiple weighted compatible worlds."""
    if n_samples < 1:
        raise ValueError(f"n_samples must be >= 1, got {n_samples}.")
    if belief_state is None:
        belief_state = build_belief_state(game_state)
    return tuple(sample_weighted_world(game_state, rng, belief_state) for _ in range(n_samples))



def _assign_unknown_cards(
    unknown_cards: list[Card],
    slot_capacity: dict[tuple[str, int | None], int],
    assignment: dict[tuple[str, int | None], list[Card]],
    belief_state: BeliefState,
    posterior,
    rng: random.Random,
) -> bool:
    if not unknown_cards:
        return all(len(assignment.get(slot, [])) == capacity for slot, capacity in slot_capacity.items())

    best_index = None
    best_destinations = None
    for idx, card in enumerate(unknown_cards):
        destinations = _allowed_destinations(card, slot_capacity, assignment, belief_state)
        if not destinations:
            return False
        if best_destinations is None or len(destinations) < len(best_destinations):
            best_index = idx
            best_destinations = destinations
            if len(best_destinations) == 1:
                break

    assert best_index is not None and best_destinations is not None
    card = unknown_cards.pop(best_index)
    ordered_destinations = _weighted_destination_order(card, best_destinations, posterior, rng)
    for destination in ordered_destinations:
        cards = assignment.setdefault(destination, [])
        cards.append(card)
        if _assign_unknown_cards(unknown_cards, slot_capacity, assignment, belief_state, posterior, rng):
            return True
        cards.pop()
    unknown_cards.insert(best_index, card)
    return False



def _allowed_destinations(
    card: Card,
    slot_capacity: dict[tuple[str, int | None], int],
    assignment: dict[tuple[str, int | None], list[Card]],
    belief_state: BeliefState,
) -> list[tuple[str, int | None]]:
    destinations: list[tuple[str, int | None]] = []
    for slot, capacity in slot_capacity.items():
        if len(assignment.get(slot, [])) >= capacity:
            continue
        slot_type, player_index = slot
        if slot_type == "dog":
            if card in belief_state.dog_impossible_cards:
                continue
            destinations.append(slot)
            continue
        assert player_index is not None
        if card in belief_state.impossible_cards_by_player[player_index]:
            continue
        destinations.append(slot)
    return destinations



def _weighted_destination_order(card, destinations, posterior, rng):
    remaining = list(destinations)
    ordered: list[tuple[str, int | None]] = []
    while remaining:
        weights = [_destination_weight(card, destination, posterior) for destination in remaining]
        destination = rng.choices(remaining, weights=weights, k=1)[0]
        ordered.append(destination)
        remaining.remove(destination)
    return ordered



def _destination_weight(card, destination, posterior) -> float:
    location_type, player_index = destination
    if location_type == "dog":
        return max(posterior.probability_card_in_dog(card), 1e-12)
    assert player_index is not None
    return max(posterior.probability_card_in_player(card, player_index), 1e-12)
