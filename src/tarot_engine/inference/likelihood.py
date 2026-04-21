"""Likelihood scoring for complete hidden worlds.

The current model intentionally stays lightweight and conservative. It does not
claim exact Bayesian correctness; instead it provides a stable plausibility
score for worlds that are already compatible with hard constraints.

The score combines:
- per-card posterior marginals from ``BeliefState.posterior``
- slot-capacity consistency already enforced by the sampler
- log-space aggregation for numerical stability

This is sufficient to support weighted hidden-world sampling and to expose a
clean extension point for richer likelihood terms later.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log

from tarot_engine.domain.cards import Card
from tarot_engine.domain.game_state import WorldState
from tarot_engine.inference.belief_state import BeliefState, build_belief_state
from tarot_engine.inference.consistency import validate_world_against_belief_state


@dataclass(frozen=True)
class WorldLikelihood:
    """Likelihood diagnostics for one complete world assignment."""

    log_weight: float
    weight: float
    card_factor_count: int

    def __post_init__(self) -> None:
        if self.weight <= 0.0:
            raise ValueError(f"weight must be > 0, got {self.weight}.")
        if self.card_factor_count < 0:
            raise ValueError(
                f"card_factor_count must be >= 0, got {self.card_factor_count}."
            )



def score_world_likelihood(
    world_state: WorldState,
    belief_state: BeliefState | None = None,
) -> WorldLikelihood:
    """Return a conservative plausibility score for one compatible world.

    The weight is the product of posterior marginals for every currently hidden
    card assignment (other players' remaining hands + dog). The observed
    player's known hand and already played cards are excluded because their
    probabilities are degenerate by construction.
    """
    game_state = world_state.game_state
    if belief_state is None:
        belief_state = build_belief_state(game_state)
    validate_world_against_belief_state(world_state, belief_state)

    posterior = belief_state.posterior
    observed = belief_state.observed_player_index
    hidden_assignments: list[tuple[Card, float]] = []

    for player_index, hand in enumerate(world_state.remaining_hands_by_player):
        if player_index == observed:
            continue
        for card in hand:
            hidden_assignments.append(
                (card, posterior.probability_card_in_player(card, player_index))
            )

    for card in world_state.dog:
        hidden_assignments.append((card, posterior.probability_card_in_dog(card)))

    log_weight = 0.0
    for card, probability in hidden_assignments:
        if probability <= 0.0:
            raise ValueError(
                f"World assigns card {card} to a zero-probability location under the posterior."
            )
        log_weight += log(probability)

    return WorldLikelihood(
        log_weight=log_weight,
        weight=exp(log_weight),
        card_factor_count=len(hidden_assignments),
    )
