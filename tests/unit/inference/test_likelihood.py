"""Tests for world likelihood scoring."""

import random

from tarot_engine.inference.belief_state import build_belief_state
from tarot_engine.inference.likelihood import score_world_likelihood
from tarot_engine.inference.sampler import sample_weighted_world
from tests.unit.inference.test_sampler import _make_sampling_state


class TestWorldLikelihood:
    def test_weighted_sample_returns_positive_likelihood(self) -> None:
        game_state = _make_sampling_state()
        belief = build_belief_state(game_state)

        sample = sample_weighted_world(game_state, random.Random(7), belief)

        assert sample.likelihood.weight > 0.0
        assert sample.likelihood.card_factor_count > 0

    def test_score_world_likelihood_is_reproducible(self) -> None:
        game_state = _make_sampling_state()
        belief = build_belief_state(game_state)
        world = sample_weighted_world(game_state, random.Random(11), belief).world_state

        likelihood_1 = score_world_likelihood(world, belief)
        likelihood_2 = score_world_likelihood(world, belief)

        assert likelihood_1 == likelihood_2
