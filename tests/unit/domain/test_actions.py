"""Tests for turn-by-turn action models."""

import pytest

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card


class TestPlayAction:
    def test_valid_play_action_constructs(self) -> None:
        action = PlayAction(player_index=2, card=Card.trump(12))
        assert action.player_index == 2
        assert action.card == Card.trump(12)

    def test_invalid_player_index_raises(self) -> None:
        with pytest.raises(ValueError, match="player_index"):
            PlayAction(player_index=5, card=Card.trump(1))
