"""Tests for turn-by-turn observation models."""

import pytest

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import CompletedTrick


class TestCardPlayedObservation:
    def test_valid_observation_constructs(self) -> None:
        observation = CardPlayedObservation(
            action=PlayAction(player_index=1, card=Card.trump(7)),
            trick_number=2,
        )
        assert observation.trick_number == 2
        assert observation.action.player_index == 1

    def test_invalid_trick_number_raises(self) -> None:
        with pytest.raises(ValueError, match="trick_number"):
            CardPlayedObservation(
                action=PlayAction(player_index=1, card=Card.trump(7)),
                trick_number=0,
            )


class TestTrickCompletedObservation:
    def test_valid_observation_constructs(self) -> None:
        trick = CompletedTrick(
            cards=(
                TrickCard(card=Card.trump(1), player_index=0),
                TrickCard(card=Card.trump(2), player_index=1),
                TrickCard(card=Card.trump(3), player_index=2),
                TrickCard(card=Card.trump(4), player_index=3),
                TrickCard(card=Card.excuse(), player_index=4),
            ),
            winner_index=3,
            lead_player_index=0,
            trick_number=1,
        )
        observation = TrickCompletedObservation(trick=trick)
        assert observation.trick.winner_index == 3
