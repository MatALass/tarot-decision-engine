"""Turn-by-turn policy interfaces and baseline implementations."""

from __future__ import annotations

from typing import Protocol

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.game_state import GameState
from tarot_engine.domain.legal_actions import legal_actions
from tarot_engine.domain.rules import Trick
from tarot_engine.simulation.policies import choose_card


class TurnPolicy(Protocol):
    """Minimal turn-by-turn policy contract."""

    def select_action(self, game_state: GameState) -> PlayAction: ...


class FirstLegalActionPolicy:
    """Deterministic baseline: select the first legal action."""

    def select_action(self, game_state: GameState) -> PlayAction:
        return legal_actions(game_state)[0]


class HeuristicTurnPolicy:
    """Adapter around the existing MVP play heuristic."""

    def select_action(self, game_state: GameState) -> PlayAction:
        legal = legal_actions(game_state)
        chosen_card = choose_card(
            player_index=game_state.context.player_index,
            legal=tuple(action.card for action in legal),
            trick=Trick(game_state.current_trick),
            taker_index=game_state.context.taker_index,
        )
        return PlayAction(player_index=game_state.context.player_index, card=chosen_card)
