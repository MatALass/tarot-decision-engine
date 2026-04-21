"""Tests for rollout from an intermediate or initial WorldState."""

from __future__ import annotations

import random

from tarot_engine.domain.enums import Contract
from tarot_engine.simulation.rollout import rollout_world
from tarot_engine.simulation.sampler import sample_deal
from tarot_engine.simulation.turn_runner import build_initial_world_state
from tests.fixtures.hands import average_hand


class TestRolloutWorld:
    def test_rollout_from_initial_world_reaches_terminal_state(self) -> None:
        deal = sample_deal(average_hand(), random.Random(7))
        world_state, initial_piles = build_initial_world_state(deal, Contract.GARDE)

        result = rollout_world(world_state)

        assert result.score.contract == Contract.GARDE
        assert all(len(hand) == 0 for hand in result.final_world_state.remaining_hands_by_player)
        assert not result.final_world_state.game_state.current_trick
        assert len(result.winner_piles_by_player[0]) >= len(initial_piles[0])
