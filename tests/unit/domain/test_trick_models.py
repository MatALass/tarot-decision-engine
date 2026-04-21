"""Tests for trick-history domain models."""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick, TrickHistory


def _make_completed_trick(trick_number: int = 1) -> CompletedTrick:
    return CompletedTrick(
        cards=(
            TrickCard(card=Card.trump(1), player_index=0),
            TrickCard(card=Card.trump(5), player_index=1),
            TrickCard(card=Card.suited(Suit.SPADES, Rank.AS), player_index=2),
            TrickCard(card=Card.suited(Suit.HEARTS, Rank.AS), player_index=3),
            TrickCard(card=Card.excuse(), player_index=4),
        ),
        winner_index=1,
        lead_player_index=0,
        trick_number=trick_number,
    )


class TestCompletedTrick:
    def test_valid_completed_trick_constructs(self) -> None:
        trick = _make_completed_trick()
        assert trick.winner_index == 1
        assert trick.lead_player_index == 0
        assert len(trick.played_cards) == 5

    def test_wrong_number_of_cards_raises(self) -> None:
        with pytest.raises(ValueError, match="exactly 5 cards"):
            CompletedTrick(
                cards=(
                    TrickCard(card=Card.trump(1), player_index=0),
                    TrickCard(card=Card.trump(5), player_index=1),
                ),
                winner_index=1,
                lead_player_index=0,
                trick_number=1,
            )

    def test_duplicate_player_indices_raise(self) -> None:
        with pytest.raises(ValueError, match="duplicate player indices"):
            CompletedTrick(
                cards=(
                    TrickCard(card=Card.trump(1), player_index=0),
                    TrickCard(card=Card.trump(5), player_index=0),
                    TrickCard(card=Card.suited(Suit.SPADES, Rank.AS), player_index=2),
                    TrickCard(card=Card.suited(Suit.HEARTS, Rank.AS), player_index=3),
                    TrickCard(card=Card.excuse(), player_index=4),
                ),
                winner_index=0,
                lead_player_index=0,
                trick_number=1,
            )

    def test_lead_player_must_match_first_card(self) -> None:
        with pytest.raises(ValueError, match="first card"):
            CompletedTrick(
                cards=_make_completed_trick().cards,
                winner_index=1,
                lead_player_index=2,
                trick_number=1,
            )


class TestTrickHistory:
    def test_valid_history_constructs(self) -> None:
        history = TrickHistory(tricks=(_make_completed_trick(1), _make_completed_trick(2)))
        assert len(history) == 2
        assert len(history.cards_played) == 10

    def test_non_contiguous_trick_numbers_raise(self) -> None:
        with pytest.raises(ValueError, match="contiguous"):
            TrickHistory(tricks=(_make_completed_trick(1), _make_completed_trick(3)))
