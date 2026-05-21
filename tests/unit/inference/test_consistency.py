"""Tests for world/belief-state consistency validation."""

import random

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory
from tarot_engine.inference.belief_state import build_belief_state
from tarot_engine.inference.consistency import validate_world_against_belief_state, world_matches_belief_state
from tarot_engine.inference.sampler import sample_compatible_world



def _make_state_for_consistency() -> GameState:
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
        current_trick=(),
        completed_tricks=TrickHistory(tricks=(completed,)),
        next_player_index=2,
    )


class TestConsistency:
    def test_validate_world_against_belief_state_accepts_matching_world(self) -> None:
        game_state = _make_state_for_consistency()
        belief = build_belief_state(game_state)
        world = sample_compatible_world(game_state, random.Random(42), belief)

        validate_world_against_belief_state(world, belief)
        assert world_matches_belief_state(world, belief) is True

    def test_validate_world_against_belief_state_rejects_forbidden_card(self) -> None:
        game_state = _make_state_for_consistency()
        belief = build_belief_state(game_state)
        world = sample_compatible_world(game_state, random.Random(42), belief)

        player_one_hand = list(world.remaining_hands_by_player[1])
        swap_source_player = None
        swap_source_card = None
        for player_index in range(2, 5):
            for card in world.remaining_hands_by_player[player_index]:
                if card.suit == Suit.HEARTS:
                    swap_source_player = player_index
                    swap_source_card = card
                    break
            if swap_source_card is not None:
                break
        assert swap_source_player is not None and swap_source_card is not None

        replacement = player_one_hand[0]
        player_one_hand[0] = swap_source_card
        source_hand = list(world.remaining_hands_by_player[swap_source_player])
        source_hand[source_hand.index(swap_source_card)] = replacement

        invalid_world = WorldState(
            game_state=game_state,
            remaining_hands_by_player=(
                world.remaining_hands_by_player[0],
                tuple(player_one_hand),
                tuple(source_hand) if swap_source_player == 2 else world.remaining_hands_by_player[2],
                tuple(source_hand) if swap_source_player == 3 else world.remaining_hands_by_player[3],
                tuple(source_hand) if swap_source_player == 4 else world.remaining_hands_by_player[4],
            ),
            dog=world.dog,
        )

        with pytest.raises(ValueError, match="forbidden by BeliefState"):
            validate_world_against_belief_state(invalid_world, belief)
        assert world_matches_belief_state(invalid_world, belief) is False
