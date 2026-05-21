"""Probabilistic posterior utilities built on top of hard-constraint belief states.

This module intentionally provides a conservative probabilistic layer without
claiming exact Bayesian inference. The current model combines:
- hard impossibility constraints from ``BeliefState``
- exact known information for the observed player's remaining hand
- slot-capacity weighting for unknown cards
- independent-card approximations for aggregate events

That is sufficient for UI / analysis use cases and for the next weighted
sampling step, while staying compatible with the current architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import N_PLAYERS
from tarot_engine.domain.enums import Suit

if TYPE_CHECKING:
    from tarot_engine.inference.belief_state import BeliefState

Location = tuple[str, int | None]


@dataclass(frozen=True)
class CardLocationProbability:
    """Probability that one card belongs to one specific location."""

    card: Card
    location_type: str
    player_index: int | None
    probability: float

    def __post_init__(self) -> None:
        if self.location_type not in {"player", "dog", "played"}:
            raise ValueError(
                f"location_type must be one of 'player', 'dog', 'played', got {self.location_type}."
            )
        if self.location_type == "player":
            if self.player_index is None or not (0 <= self.player_index < N_PLAYERS):
                raise ValueError("player_index must be a valid player for location_type='player'.")
        else:
            if self.player_index is not None:
                raise ValueError(
                    "player_index must be None for location_type='dog' or 'played'."
                )
        if not (0.0 <= self.probability <= 1.0):
            raise ValueError(f"probability must be in [0, 1], got {self.probability}.")


@dataclass(frozen=True)
class Posterior:
    """Probabilistic view derived from a ``BeliefState``.

    The posterior is intentionally represented as per-card marginals. Aggregate
    queries such as "player i is void in suit S" or "player i has at least k
    trumps" are derived from those marginals using standard independent-event
    approximations.
    """

    belief_state: BeliefState

    def __post_init__(self) -> None:
        for card, mapping in self.card_location_probabilities.items():
            total = sum(mapping.values())
            if abs(total - 1.0) > 1e-9:
                raise ValueError(
                    f"Card {card} posterior probabilities must sum to 1.0, got {total}."
                )

    @cached_property
    def card_location_probabilities(self) -> dict[Card, dict[Location, float]]:
        return _build_card_location_probabilities(self.belief_state)

    def probability_card_in_player(self, card: Card, player_index: int) -> float:
        if not (0 <= player_index < N_PLAYERS):
            raise ValueError(
                f"player_index must be in [0, {N_PLAYERS - 1}], got {player_index}."
            )
        return self.card_location_probabilities[card].get(("player", player_index), 0.0)

    def probability_card_in_dog(self, card: Card) -> float:
        return self.card_location_probabilities[card].get(("dog", None), 0.0)

    def probability_card_played(self, card: Card) -> float:
        return self.card_location_probabilities[card].get(("played", None), 0.0)

    def distribution_for_card(self, card: Card) -> tuple[CardLocationProbability, ...]:
        mapping = self.card_location_probabilities[card]
        entries = [
            CardLocationProbability(
                card=card,
                location_type=location_type,
                player_index=player_index,
                probability=probability,
            )
            for (location_type, player_index), probability in mapping.items()
        ]
        return tuple(sorted(entries, key=lambda item: (item.location_type, item.player_index or -1)))

    def probability_player_void_in_suit(self, player_index: int, suit: Suit) -> float:
        if not (0 <= player_index < N_PLAYERS):
            raise ValueError(
                f"player_index must be in [0, {N_PLAYERS - 1}], got {player_index}."
            )
        if suit in self.belief_state.hard_constraints.void_suits_by_player[player_index]:
            return 1.0

        if player_index == self.belief_state.observed_player_index:
            return 0.0 if any(card.suit == suit for card in self.belief_state.known_remaining_hand) else 1.0

        probs = [
            self.probability_card_in_player(card, player_index)
            for card in self.belief_state.unknown_cards
            if card.suit == suit
        ]
        void_probability = 1.0
        for probability in probs:
            void_probability *= 1.0 - probability
        return max(0.0, min(1.0, void_probability))

    def probability_player_has_at_least_n_trumps(self, player_index: int, n_trumps: int) -> float:
        if not (0 <= player_index < N_PLAYERS):
            raise ValueError(
                f"player_index must be in [0, {N_PLAYERS - 1}], got {player_index}."
            )
        if n_trumps <= 0:
            return 1.0
        known_trumps = 0
        trump_probabilities: list[float] = []

        if player_index == self.belief_state.observed_player_index:
            known_trumps = sum(1 for card in self.belief_state.known_remaining_hand if card.is_trump)
        else:
            for card in self.belief_state.unknown_cards:
                if card.is_trump:
                    probability = self.probability_card_in_player(card, player_index)
                    if probability > 0.0:
                        trump_probabilities.append(probability)

        if known_trumps >= n_trumps:
            return 1.0
        needed = n_trumps - known_trumps
        if not trump_probabilities:
            return 0.0
        distribution = _poisson_binomial_distribution(trump_probabilities)
        return float(sum(distribution[needed:]))



def build_posterior(belief_state: BeliefState) -> Posterior:
    """Build a probabilistic posterior view from a BeliefState."""
    return Posterior(belief_state=belief_state)



def _build_card_location_probabilities(
    belief_state: BeliefState,
) -> dict[Card, dict[Location, float]]:
    mapping: dict[Card, dict[Location, float]] = {}
    capacities = _location_capacities(belief_state)
    observed = belief_state.observed_player_index

    for card in belief_state.known_remaining_hand:
        mapping[card] = {("player", observed): 1.0}

    for card in belief_state.played_cards:
        mapping[card] = {("played", None): 1.0}

    for card in belief_state.unknown_cards:
        allowed = _allowed_locations(card, belief_state)
        total_weight = sum(capacities[location] for location in allowed)
        if total_weight <= 0:
            raise ValueError(f"No positive-capacity location available for unknown card {card}.")
        mapping[card] = {
            location: capacities[location] / total_weight
            for location in allowed
        }

    return mapping



def _location_capacities(belief_state: BeliefState) -> dict[Location, int]:
    capacities: dict[Location, int] = {("dog", None): belief_state.dog_card_count}
    for player_index, count in enumerate(belief_state.remaining_card_counts_by_player):
        capacities[("player", player_index)] = count
    return capacities



def _allowed_locations(card: Card, belief_state: BeliefState) -> tuple[Location, ...]:
    allowed: list[Location] = []
    for player_index in range(N_PLAYERS):
        if card not in belief_state.impossible_cards_by_player[player_index]:
            allowed.append(("player", player_index))
    if card not in belief_state.dog_impossible_cards:
        allowed.append(("dog", None))
    return tuple(allowed)



def _poisson_binomial_distribution(probabilities: list[float]) -> list[float]:
    distribution = [1.0]
    for probability in probabilities:
        next_distribution = [0.0] * (len(distribution) + 1)
        for k, mass in enumerate(distribution):
            next_distribution[k] += mass * (1.0 - probability)
            next_distribution[k + 1] += mass * probability
        distribution = next_distribution
    return distribution
