"""Tests for pure state-transition functions."""

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.transitions import apply_play_action, apply_play_action_world
from tarot_engine.domain.trick import TrickHistory


class TestApplyPlayAction:
    def test_observed_player_play_updates_remaining_hand_and_current_trick(self) -> None:
        deck = generate_deck()
        hand_cards = tuple(deck[:15])
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(hand_cards)),
        )
        state = GameState(
            context=context,
            remaining_hand=hand_cards,
            current_trick=(),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=0,
        )

        next_state, observations = apply_play_action(
            state,
            PlayAction(player_index=0, card=hand_cards[0]),
        )

        assert len(next_state.remaining_hand) == 14
        assert next_state.current_trick == (TrickCard(card=hand_cards[0], player_index=0),)
        assert next_state.next_player_index == 1
        assert len(observations) == 1
        assert isinstance(observations[0], CardPlayedObservation)

    def test_wrong_player_cannot_act(self) -> None:
        deck = generate_deck()
        hand_cards = tuple(deck[:15])
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(hand_cards)),
        )
        state = GameState(
            context=context,
            remaining_hand=hand_cards,
            current_trick=(),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=0,
        )

        try:
            apply_play_action(state, PlayAction(player_index=1, card=deck[15]))
        except ValueError as exc:
            assert "does not match next_player_index" in str(exc)
        else:
            raise AssertionError("Expected ValueError")

    def test_completed_trick_resets_current_trick_and_emits_completion(self) -> None:
        deck = generate_deck()
        hand_cards = tuple(deck[:15])
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(hand_cards)),
        )
        state = GameState(
            context=context,
            remaining_hand=tuple(hand_cards[1:]),
            current_trick=(
                TrickCard(card=hand_cards[0], player_index=0),
                TrickCard(card=deck[15], player_index=1),
                TrickCard(card=deck[16], player_index=2),
                TrickCard(card=deck[17], player_index=3),
            ),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=4,
        )

        next_state, observations = apply_play_action(
            state,
            PlayAction(player_index=4, card=deck[18]),
        )

        assert next_state.current_trick == ()
        assert len(next_state.completed_tricks.tricks) == 1
        assert len(observations) == 2
        assert isinstance(observations[0], CardPlayedObservation)
        assert isinstance(observations[1], TrickCompletedObservation)
        assert next_state.next_player_index == observations[1].trick.winner_index


class TestApplyPlayActionWorld:
    def test_world_transition_removes_card_from_real_hand(self) -> None:
        deck = generate_deck()
        hand_cards = tuple(deck[:15])
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(hand_cards)),
        )
        game_state = GameState(
            context=context,
            remaining_hand=hand_cards,
            current_trick=(),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=0,
        )
        world_state = WorldState(
            game_state=game_state,
            remaining_hands_by_player=(
                hand_cards,
                tuple(deck[15:30]),
                tuple(deck[30:45]),
                tuple(deck[45:60]),
                tuple(deck[60:75]),
            ),
            dog=tuple(deck[75:78]),
        )

        next_world, observations = apply_play_action_world(
            world_state,
            PlayAction(player_index=0, card=hand_cards[0]),
        )

        assert len(next_world.remaining_hands_by_player[0]) == 14
        assert hand_cards[0] not in next_world.remaining_hands_by_player[0]
        assert len(observations) == 1

    def test_world_transition_rejects_card_not_in_players_real_hand(self) -> None:
        deck = generate_deck()
        hand_cards = tuple(deck[:15])
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(hand_cards)),
        )
        game_state = GameState(
            context=context,
            remaining_hand=hand_cards,
            current_trick=(),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=1,
        )
        world_state = WorldState(
            game_state=game_state,
            remaining_hands_by_player=(
                hand_cards,
                tuple(deck[15:30]),
                tuple(deck[30:45]),
                tuple(deck[45:60]),
                tuple(deck[60:75]),
            ),
            dog=tuple(deck[75:78]),
        )

        try:
            apply_play_action_world(world_state, PlayAction(player_index=1, card=deck[0]))
        except ValueError as exc:
            assert "not in their remaining hand" in str(exc)
        else:
            raise AssertionError("Expected ValueError")
