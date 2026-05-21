"""Tests for hard inference constraints derived from observable play."""

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory
from tarot_engine.inference.constraints import derive_hard_constraints



def _make_inference_game_state() -> GameState:
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


class TestHardConstraints:
    def test_derive_constraints_detects_void_suit_and_no_trumps(self) -> None:
        game_state = _make_inference_game_state()

        constraints = derive_hard_constraints(game_state)

        assert Suit.HEARTS in constraints.void_suits_by_player[1]
        assert constraints.no_trumps_by_player[1] is True
        assert constraints.no_trumps_by_player[3] is True
        assert Card.suited(Suit.HEARTS, Rank.ROI) in constraints.impossible_cards_by_player[1]
        assert Card.trump(21) in constraints.impossible_cards_by_player[1]

    def test_derive_constraints_detects_undercut_upper_bound(self) -> None:
        game_state = _make_inference_game_state()

        constraints = derive_hard_constraints(game_state)

        assert Card.trump(11) in constraints.impossible_cards_by_player[4]
        assert Card.trump(21) in constraints.impossible_cards_by_player[4]
        assert Card.trump(9) not in constraints.impossible_cards_by_player[4]
