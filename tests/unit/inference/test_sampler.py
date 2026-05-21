"""Tests for compatible hidden-world sampling."""

import random

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory
from tarot_engine.inference.belief_state import build_belief_state
from tarot_engine.inference.consistency import world_matches_belief_state
from tarot_engine.inference.sampler import (
    sample_compatible_world,
    sample_compatible_worlds,
    sample_weighted_world,
    sample_weighted_worlds,
)



def _make_sampling_state() -> GameState:
    observed_initial_cards = (
        Card.suited(Suit.HEARTS, Rank.AS),
        Card.suited(Suit.SPADES, Rank.AS),
        Card.suited(Suit.DIAMONDS, Rank.AS),
        Card.suited(Suit.CLUBS, Rank.AS),
        Card.trump(1),
        Card.trump(2),
        Card.trump(3),
        Card.trump(4),
        Card.trump(5),
        Card.trump(6),
        Card.trump(7),
        Card.trump(12),
        Card.trump(13),
        Card.trump(14),
        Card.excuse(),
    )
    context = InitialDealContext(
        player_index=0,
        taker_index=0,
        contract=Contract.GARDE,
        initial_hand=Hand.from_cards(list(observed_initial_cards)),
    )
    completed = CompletedTrick(
        cards=(
            TrickCard(card=Card.suited(Suit.HEARTS, Rank.AS), player_index=0),
            TrickCard(card=Card.suited(Suit.CLUBS, Rank.TWO), player_index=1),
            TrickCard(card=Card.trump(10), player_index=2),
            TrickCard(card=Card.suited(Suit.HEARTS, Rank.TWO), player_index=3),
            TrickCard(card=Card.trump(8), player_index=4),
        ),
        winner_index=2,
        lead_player_index=0,
        trick_number=1,
    )
    return GameState(
        context=context,
        remaining_hand=tuple(card for card in observed_initial_cards if card != Card.suited(Suit.HEARTS, Rank.AS)),
        current_trick=(
            TrickCard(card=Card.trump(11), player_index=2),
            TrickCard(card=Card.suited(Suit.SPADES, Rank.TWO), player_index=3),
        ),
        completed_tricks=TrickHistory(tricks=(completed,)),
        next_player_index=4,
    )


class TestSampler:
    def test_sample_compatible_world_respects_belief_state(self) -> None:
        game_state = _make_sampling_state()
        belief = build_belief_state(game_state)

        world = sample_compatible_world(game_state, random.Random(7), belief)

        assert tuple(world.remaining_hands_by_player[0]) == game_state.remaining_hand
        assert len(world.dog) == 3
        assert all(len(hand) == belief.remaining_card_counts_by_player[i] for i, hand in enumerate(world.remaining_hands_by_player))
        assert world_matches_belief_state(world, belief) is True

    def test_sample_compatible_worlds_returns_requested_number(self) -> None:
        game_state = _make_sampling_state()

        worlds = sample_compatible_worlds(game_state, n_samples=3, rng=random.Random(9))

        assert len(worlds) == 3
        assert all(world.game_state == game_state for world in worlds)


    def test_weighted_world_sampling_returns_likelihoods(self) -> None:
        game_state = _make_sampling_state()

        samples = sample_weighted_worlds(game_state, n_samples=2, rng=random.Random(19))

        assert len(samples) == 2
        assert all(sample.likelihood.weight > 0.0 for sample in samples)
        assert all(sample.world_state.game_state == game_state for sample in samples)
