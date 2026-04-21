"""Tests for WorldState -> GameState projections."""

from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.projections import build_all_game_states, build_game_state
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory


def _make_world_state() -> WorldState:
    deck = generate_deck()
    initial_hands = (
        tuple(deck[:15]),
        tuple(deck[15:30]),
        tuple(deck[30:45]),
        tuple(deck[45:60]),
        tuple(deck[60:75]),
    )
    completed = CompletedTrick(
        cards=(
            TrickCard(card=initial_hands[0][0], player_index=0),
            TrickCard(card=initial_hands[1][0], player_index=1),
            TrickCard(card=initial_hands[2][0], player_index=2),
            TrickCard(card=initial_hands[3][0], player_index=3),
            TrickCard(card=initial_hands[4][0], player_index=4),
        ),
        winner_index=0,
        lead_player_index=0,
        trick_number=1,
    )
    current_trick = (
        TrickCard(card=initial_hands[1][1], player_index=1),
        TrickCard(card=initial_hands[0][1], player_index=0),
    )
    remaining_hands = (
        tuple(initial_hands[0][2:]),
        tuple(initial_hands[1][2:]),
        tuple(initial_hands[2][1:]),
        tuple(initial_hands[3][1:]),
        tuple(initial_hands[4][1:]),
    )
    context = InitialDealContext(
        player_index=0,
        taker_index=0,
        contract=Contract.GARDE_SANS,
        initial_hand=Hand.from_cards(list(initial_hands[0])),
        partner_index=None,
    )
    game_state = GameState(
        context=context,
        remaining_hand=remaining_hands[0],
        current_trick=current_trick,
        completed_tricks=TrickHistory(tricks=(completed,)),
        next_player_index=2,
    )
    return WorldState(game_state=game_state, remaining_hands_by_player=remaining_hands)


class TestBuildGameState:
    def test_build_game_state_reconstructs_initial_hand_for_any_player(self) -> None:
        world = _make_world_state()

        state = build_game_state(world, 1)

        assert state.context.player_index == 1
        assert len(state.context.initial_hand) == 15
        assert set(state.remaining_hand) == set(world.remaining_hands_by_player[1])
        assert state.current_trick == world.game_state.current_trick
        assert state.completed_tricks == world.game_state.completed_tricks

    def test_build_all_game_states_returns_one_per_player(self) -> None:
        world = _make_world_state()

        states = build_all_game_states(world)

        assert len(states) == 5
        assert tuple(state.context.player_index for state in states) == (0, 1, 2, 3, 4)
