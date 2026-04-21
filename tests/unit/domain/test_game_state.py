"""Tests for InitialDealContext, GameState, and WorldState."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory


def _make_initial_context() -> InitialDealContext:
    deck = generate_deck()
    initial_hand = Hand.from_cards(list(deck[:15]))
    return InitialDealContext(
        player_index=0,
        taker_index=0,
        contract=Contract.GARDE,
        initial_hand=initial_hand,
    )


def _make_completed_trick() -> CompletedTrick:
    deck = generate_deck()
    return CompletedTrick(
        cards=(
            TrickCard(card=deck[0], player_index=0),
            TrickCard(card=deck[15], player_index=1),
            TrickCard(card=deck[16], player_index=2),
            TrickCard(card=deck[17], player_index=3),
            TrickCard(card=deck[18], player_index=4),
        ),
        winner_index=1,
        lead_player_index=0,
        trick_number=1,
    )


class TestInitialDealContext:
    def test_valid_context_constructs(self) -> None:
        context = _make_initial_context()
        assert context.player_index == 0
        assert context.contract == Contract.GARDE

    def test_invalid_player_index_raises(self) -> None:
        hand = Hand.from_cards(list(generate_deck()[:15]))
        with pytest.raises(ValueError, match="player_index"):
            InitialDealContext(
                player_index=5,
                taker_index=0,
                contract=Contract.PRISE,
                initial_hand=hand,
            )


class TestGameState:
    def test_valid_game_state_constructs(self) -> None:
        context = _make_initial_context()
        history = TrickHistory(tricks=(_make_completed_trick(),))
        remaining_hand = tuple(card for card in context.initial_hand.cards if card != generate_deck()[0])
        state = GameState(
            context=context,
            remaining_hand=remaining_hand,
            current_trick=(),
            completed_tricks=history,
            next_player_index=1,
        )
        assert len(state.remaining_hand) == 14
        assert len(state.played_cards) == 5

    def test_remaining_hand_with_duplicates_raises(self) -> None:
        context = _make_initial_context()
        card = next(iter(context.initial_hand.cards))
        with pytest.raises(ValueError, match="duplicate"):
            GameState(
                context=context,
                remaining_hand=(card, card),
                current_trick=(),
                completed_tricks=TrickHistory(tricks=()),
                next_player_index=0,
            )

    def test_current_trick_size_above_four_raises(self) -> None:
        context = _make_initial_context()
        current_trick = tuple(
            TrickCard(card=generate_deck()[15 + i], player_index=i)
            for i in range(5)
        )
        with pytest.raises(ValueError, match="current_trick size"):
            GameState(
                context=context,
                remaining_hand=tuple(context.initial_hand.cards),
                current_trick=current_trick,
                completed_tricks=TrickHistory(tricks=()),
                next_player_index=0,
            )

    def test_remaining_hand_overlapping_played_cards_raises(self) -> None:
        context = _make_initial_context()
        played = next(iter(context.initial_hand.cards))
        with pytest.raises(ValueError, match="already played"):
            GameState(
                context=context,
                remaining_hand=tuple(context.initial_hand.cards),
                current_trick=(TrickCard(card=played, player_index=0),),
                completed_tricks=TrickHistory(tricks=()),
                next_player_index=1,
            )


class TestWorldState:
    def test_valid_world_state_constructs(self) -> None:
        context = _make_initial_context()
        history = TrickHistory(tricks=(_make_completed_trick(),))
        remaining_hand = tuple(card for card in context.initial_hand.cards if card != generate_deck()[0])
        game_state = GameState(
            context=context,
            remaining_hand=remaining_hand,
            current_trick=(),
            completed_tricks=history,
            next_player_index=1,
        )
        deck = generate_deck()
        world = WorldState(
            game_state=game_state,
            remaining_hands_by_player=(
                remaining_hand,
                tuple(deck[19:33]),
                tuple(deck[33:48]),
                tuple(deck[48:63]),
                tuple(deck[63:78]),
            ),
        )
        assert len(world.remaining_hands_by_player) == 5

    def test_global_duplicate_cards_raise(self) -> None:
        context = _make_initial_context()
        history = TrickHistory(tricks=(_make_completed_trick(),))
        remaining_hand = tuple(card for card in context.initial_hand.cards if card != generate_deck()[0])
        game_state = GameState(
            context=context,
            remaining_hand=remaining_hand,
            current_trick=(),
            completed_tricks=history,
            next_player_index=1,
        )
        duplicate_card = generate_deck()[19]
        with pytest.raises(ValueError, match="duplicate cards"):
            WorldState(
                game_state=game_state,
                remaining_hands_by_player=(
                    remaining_hand,
                    (duplicate_card,),
                    (duplicate_card,),
                    (),
                    (),
                ),
            )

    def test_observed_player_hand_must_match_game_state(self) -> None:
        context = _make_initial_context()
        history = TrickHistory(tricks=(_make_completed_trick(),))
        remaining_hand = tuple(card for card in context.initial_hand.cards if card != generate_deck()[0])
        game_state = GameState(
            context=context,
            remaining_hand=remaining_hand,
            current_trick=(),
            completed_tricks=history,
            next_player_index=1,
        )
        with pytest.raises(ValueError, match="must match GameState.remaining_hand"):
            WorldState(
                game_state=game_state,
                remaining_hands_by_player=(
                    (),
                    (),
                    (),
                    (),
                    (),
                ),
            )
