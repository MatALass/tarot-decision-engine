"""Tests for probabilistic posterior queries built from belief states."""

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory
from tarot_engine.inference.belief_state import build_belief_state
from tarot_engine.inference.posterior import build_posterior



def _make_posterior_game_state() -> GameState:
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
        remaining_hand=tuple(
            card for card in observed_initial_cards if card != Card.suited(Suit.HEARTS, Rank.AS)
        ),
        current_trick=(
            TrickCard(card=Card.trump(11), player_index=2),
            TrickCard(card=Card.suited(Suit.SPADES, Rank.TWO), player_index=3),
        ),
        completed_tricks=TrickHistory(tricks=(completed,)),
        next_player_index=4,
    )


class TestPosterior:
    def test_known_and_played_card_probabilities_are_deterministic(self) -> None:
        belief = build_belief_state(_make_posterior_game_state())
        posterior = build_posterior(belief)

        known_card = Card.trump(1)
        played_card = Card.trump(10)

        assert posterior.probability_card_in_player(known_card, 0) == 1.0
        assert posterior.probability_card_in_dog(known_card) == 0.0
        assert posterior.probability_card_played(played_card) == 1.0
        assert posterior.probability_card_in_player(played_card, 2) == 0.0

    def test_unknown_card_distribution_sums_to_one(self) -> None:
        belief = build_belief_state(_make_posterior_game_state())
        posterior = build_posterior(belief)

        unknown_card = Card.suited(Suit.DIAMONDS, Rank.TWO)
        total = sum(item.probability for item in posterior.distribution_for_card(unknown_card))

        assert abs(total - 1.0) < 1e-9

    def test_void_probability_uses_hard_constraint(self) -> None:
        belief = build_belief_state(_make_posterior_game_state())
        posterior = build_posterior(belief)

        assert posterior.probability_player_void_in_suit(1, Suit.HEARTS) == 1.0
        assert posterior.probability_player_void_in_suit(0, Suit.SPADES) == 0.0

    def test_trump_count_probability_respects_no_trump_constraint(self) -> None:
        belief = build_belief_state(_make_posterior_game_state())
        posterior = build_posterior(belief)

        assert posterior.probability_player_has_at_least_n_trumps(1, 1) == 0.0
        assert posterior.probability_player_has_at_least_n_trumps(0, 1) == 1.0
        assert posterior.probability_player_has_at_least_n_trumps(0, 20) == 0.0

    def test_belief_state_exposes_posterior_property(self) -> None:
        belief = build_belief_state(_make_posterior_game_state())

        posterior = belief.posterior

        assert posterior.belief_state == belief
