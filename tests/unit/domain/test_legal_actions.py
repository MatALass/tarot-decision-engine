"""Tests for legal PlayAction generation."""

import pytest

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.legal_actions import legal_actions, legal_actions_world
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import TrickHistory


class TestLegalActions:
    def test_legal_actions_returns_play_actions_for_observed_player(self) -> None:
        hand_cards = (
            Card.suited(Suit.HEARTS, Rank.AS),
            Card.suited(Suit.HEARTS, Rank.ROI),
            Card.trump(5),
        )
        filler = tuple(card for card in generate_deck() if card not in hand_cards and not card.is_excuse)[:12]
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(filler) + list(hand_cards)),
        )
        full_hand = tuple(filler) + hand_cards
        state = GameState(
            context=context,
            remaining_hand=full_hand,
            current_trick=(TrickCard(card=Card.suited(Suit.HEARTS, Rank.TWO), player_index=3),),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=0,
        )

        actions = legal_actions(state)

        assert actions == (
            PlayAction(player_index=0, card=Card.suited(Suit.HEARTS, Rank.AS)),
            PlayAction(player_index=0, card=Card.suited(Suit.HEARTS, Rank.ROI)),
        )

    def test_legal_actions_raises_when_not_observed_players_turn(self) -> None:
        deck = generate_deck()
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(deck[:15])),
        )
        state = GameState(
            context=context,
            remaining_hand=tuple(deck[:15]),
            current_trick=(),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=1,
        )

        with pytest.raises(ValueError, match="only defined"):
            legal_actions(state)

    def test_legal_actions_world_uses_real_next_players_hand(self) -> None:
        deck = generate_deck()
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(deck[:15])),
        )
        game_state = GameState(
            context=context,
            remaining_hand=tuple(deck[1:15]),
            current_trick=(TrickCard(card=deck[0], player_index=0),),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=1,
        )
        world = WorldState(
            game_state=game_state,
            remaining_hands_by_player=(
                tuple(deck[1:15]),
                tuple(deck[15:30]),
                tuple(deck[30:45]),
                tuple(deck[45:60]),
                tuple(deck[60:75]),
            ),
            dog=tuple(deck[75:78]),
        )

        actions = legal_actions_world(world)

        assert actions
        assert all(action.player_index == 1 for action in actions)
