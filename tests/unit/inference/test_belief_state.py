"""Tests for minimal belief-state construction and updates."""

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.trick import TrickHistory
from tarot_engine.domain.transitions import apply_play_action
from tarot_engine.inference.belief_state import build_belief_state
from tarot_engine.inference.updater import update_belief_state



def _make_simple_state() -> GameState:
    initial_cards = (
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
        Card.trump(8),
        Card.trump(9),
        Card.trump(10),
        Card.excuse(),
    )
    context = InitialDealContext(
        player_index=0,
        taker_index=0,
        contract=Contract.GARDE,
        initial_hand=Hand.from_cards(list(initial_cards)),
    )
    return GameState(
        context=context,
        remaining_hand=initial_cards,
        current_trick=(),
        completed_tricks=TrickHistory(tricks=()),
        next_player_index=0,
    )


class TestBeliefState:
    def test_build_belief_state_counts_unknown_cards(self) -> None:
        belief = build_belief_state(_make_simple_state())

        assert belief.remaining_card_counts_by_player == (15, 15, 15, 15, 15)
        assert belief.dog_card_count == 3
        assert len(belief.unknown_cards) == 63
        assert set(belief.possible_cards_for_player(0)) == set(belief.known_remaining_hand)

    def test_update_belief_state_recomputes_after_play(self) -> None:
        game_state = _make_simple_state()
        next_state, observations = apply_play_action(
            game_state,
            PlayAction(player_index=0, card=Card.suited(Suit.HEARTS, Rank.AS)),
        )
        previous = build_belief_state(game_state)

        updated = update_belief_state(previous, next_state, observations)

        assert len(updated.known_remaining_hand) == 14
        assert Card.suited(Suit.HEARTS, Rank.AS) in updated.played_cards
        assert updated.remaining_card_counts_by_player[0] == 14
