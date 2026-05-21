"""Tests for Monte Carlo action evaluation."""

from __future__ import annotations

import random

from tarot_engine.decision.move_policies import ExpectedScoreMovePolicy
from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract, Rank, Suit
from tarot_engine.domain.game_state import GameState, InitialDealContext
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.legal_actions import legal_actions
from tarot_engine.domain.rules import TrickCard
from tarot_engine.domain.trick import TrickHistory
from tarot_engine.simulation.action_evaluator import EvaluatorConfig, evaluate_actions
from tarot_engine.simulation.sampler import sample_deal
from tarot_engine.simulation.turn_runner import build_initial_world_state
from tests.fixtures.hands import average_hand


class TestEvaluateActions:
    def test_single_legal_action_is_evaluated(self) -> None:
        deck = generate_deck()
        only_heart = Card.suited(Suit.HEARTS, Rank.AS)
        fillers = tuple(
            card
            for card in deck
            if card != only_heart and card.suit != Suit.HEARTS and not card.is_excuse
        )[:14]
        full_hand = (only_heart,) + fillers
        context = InitialDealContext(
            player_index=0,
            taker_index=0,
            contract=Contract.GARDE,
            initial_hand=Hand.from_cards(list(full_hand)),
        )
        state = GameState(
            context=context,
            remaining_hand=full_hand,
            current_trick=(
                TrickCard(card=Card.suited(Suit.HEARTS, Rank.TWO), player_index=4),
            ),
            completed_tricks=TrickHistory(tricks=()),
            next_player_index=0,
        )

        actions = legal_actions(state)
        evaluations = evaluate_actions(
            state,
            config=EvaluatorConfig(n_samples=3, seed=11),
            candidate_actions=actions,
        )

        assert actions == (PlayAction(player_index=0, card=only_heart),)
        assert len(evaluations) == 1
        assert evaluations[0].action == actions[0]
        assert evaluations[0].n_samples == 3

    def test_multiple_actions_are_ranked_consistently(self) -> None:
        deal = sample_deal(average_hand(), random.Random(123))
        world_state, _ = build_initial_world_state(deal, Contract.GARDE)
        game_state = world_state.game_state
        candidate_actions = legal_actions(game_state)[:3]

        evaluations = evaluate_actions(
            game_state,
            config=EvaluatorConfig(n_samples=4, seed=21),
            candidate_actions=candidate_actions,
        )
        recommendation = ExpectedScoreMovePolicy().choose(evaluations)

        sorted_by_ev = sorted(
            evaluations,
            key=lambda ev: (-ev.expected_score, -ev.win_rate, str(ev.action.card)),
        )
        assert len(evaluations) == 3
        assert recommendation.recommended_action == sorted_by_ev[0].action
        assert tuple(r.evaluation.action for r in recommendation.ranked_actions) == tuple(
            ev.action for ev in sorted_by_ev
        )

    def test_reproducible_with_same_seed(self) -> None:
        deal = sample_deal(average_hand(), random.Random(99))
        world_state, _ = build_initial_world_state(deal, Contract.GARDE)
        game_state = world_state.game_state
        candidate_actions = legal_actions(game_state)[:2]

        evaluations_1 = evaluate_actions(
            game_state,
            config=EvaluatorConfig(n_samples=3, seed=5),
            candidate_actions=candidate_actions,
        )
        evaluations_2 = evaluate_actions(
            game_state,
            config=EvaluatorConfig(n_samples=3, seed=5),
            candidate_actions=candidate_actions,
        )

        assert evaluations_1 == evaluations_2


    def test_evaluations_include_robust_metrics(self) -> None:
        deal = sample_deal(average_hand(), random.Random(321))
        world_state, _ = build_initial_world_state(deal, Contract.GARDE)
        game_state = world_state.game_state
        candidate_actions = legal_actions(game_state)[:2]

        evaluations = evaluate_actions(
            game_state,
            config=EvaluatorConfig(n_samples=3, seed=17),
            candidate_actions=candidate_actions,
        )

        assert all(ev.robust_score == ev.score_q10 for ev in evaluations)
        assert all(ev.downside_risk >= 0.0 for ev in evaluations)
        assert all(ev.score_q05 <= ev.score_q10 <= ev.score_q90 <= ev.score_q95 for ev in evaluations)
