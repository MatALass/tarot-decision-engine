"""Tests for turn-by-turn policies."""

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import TrickHistory
from tarot_engine.simulation.turn_policies import FirstLegalActionPolicy, HeuristicTurnPolicy


class TestFirstLegalActionPolicy:
    def test_select_action_returns_first_legal_action(self) -> None:
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

        action = FirstLegalActionPolicy().select_action(state)

        assert action == PlayAction(player_index=0, card=Card.suited(Suit.HEARTS, Rank.AS))


class TestHeuristicTurnPolicy:
    def test_select_action_uses_existing_heuristic(self) -> None:
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

        action = HeuristicTurnPolicy().select_action(state)

        assert action.player_index == 0
        assert action.card in hand_cards
