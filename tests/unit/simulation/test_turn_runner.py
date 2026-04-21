"""Tests for the turn-by-turn runner."""

import random

from tarot_engine.domain.enums import Contract
from tarot_engine.simulation.game_runner import run_deal
from tarot_engine.simulation.sampler import sample_deal
from tarot_engine.simulation.turn_runner import (
    build_initial_world_state,
    is_terminal_world_state,
    run_sampled_deal_turn_by_turn,
)
from tests.fixtures.hands import average_hand


class TestBuildInitialWorldState:
    def test_build_initial_world_state_keeps_five_hands_of_fifteen_for_garde(self) -> None:
        deal = sample_deal(average_hand(), random.Random(0))

        world_state, winner_piles = build_initial_world_state(deal, Contract.GARDE)

        assert len(world_state.remaining_hands_by_player) == 5
        assert all(len(hand) == 15 for hand in world_state.remaining_hands_by_player)
        assert len(world_state.dog) == 3
        assert len(winner_piles[0]) == 3


class TestRunSampledDealTurnByTurn:
    def test_run_matches_existing_game_runner_with_same_heuristic(self) -> None:
        deal = sample_deal(average_hand(), random.Random(123))

        legacy_result = run_deal(deal, Contract.GARDE)
        turn_result = run_sampled_deal_turn_by_turn(deal, Contract.GARDE)

        assert turn_result.score == legacy_result
        assert is_terminal_world_state(turn_result.final_world_state)
        assert len(turn_result.observations) >= 75
