"""Monte Carlo action evaluation from an observable turn-by-turn state."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from tarot_engine.domain.actions import PlayAction
from tarot_engine.domain.game_state import GameState
from tarot_engine.domain.legal_actions import legal_actions
from tarot_engine.domain.transitions import apply_play_action_world
from tarot_engine.inference.belief_state import BeliefState, build_belief_state
from tarot_engine.inference.sampler import sample_weighted_world
from tarot_engine.simulation.rollout import RolloutResult, rollout_world
from tarot_engine.simulation.turn_policies import HeuristicTurnPolicy, TurnPolicy
from tarot_engine.utils.random import make_rng


@dataclass(frozen=True)
class ActionEvaluation:
    """Aggregated Monte Carlo statistics for one candidate PlayAction."""

    action: PlayAction
    n_samples: int
    win_rate: float
    expected_score: float
    robust_score: float
    downside_risk: float
    score_std: float
    score_min: int
    score_max: int
    score_q05: float
    score_q10: float
    score_q50: float
    score_q90: float
    score_q95: float

    def __post_init__(self) -> None:
        if self.n_samples < 1:
            raise ValueError(f"n_samples must be >= 1, got {self.n_samples}.")
        if not (0.0 <= self.win_rate <= 1.0):
            raise ValueError(f"win_rate must be in [0, 1], got {self.win_rate}.")
        if self.score_std < 0:
            raise ValueError(f"score_std must be >= 0, got {self.score_std}.")
        if self.downside_risk < 0:
            raise ValueError(f"downside_risk must be >= 0, got {self.downside_risk}.")
        ordered = [
            float(self.score_min),
            self.score_q05,
            self.score_q10,
            self.score_q50,
            self.score_q90,
            self.score_q95,
            float(self.score_max),
        ]
        if any(left > right + 1e-9 for left, right in zip(ordered, ordered[1:])):
            raise ValueError("ActionEvaluation quantiles are not ordered correctly.")
        if not (self.score_min - 1e-9 <= self.expected_score <= self.score_max + 1e-9):
            raise ValueError("expected_score must lie within [score_min, score_max].")
        if not (self.score_min - 1e-9 <= self.robust_score <= self.score_max + 1e-9):
            raise ValueError("robust_score must lie within [score_min, score_max].")


@dataclass(frozen=True)
class RankedAction:
    """One evaluated action in a ranked recommendation."""

    rank: int
    evaluation: ActionEvaluation

    def __post_init__(self) -> None:
        if self.rank < 1:
            raise ValueError(f"rank must be >= 1, got {self.rank}.")


@dataclass(frozen=True)
class MoveRecommendation:
    """Recommended action plus full ranked alternatives."""

    recommended_action: PlayAction
    policy_name: str
    ranked_actions: tuple[RankedAction, ...]
    rationale: str

    def __post_init__(self) -> None:
        if not self.ranked_actions:
            raise ValueError("ranked_actions must not be empty.")
        if self.ranked_actions[0].evaluation.action != self.recommended_action:
            raise ValueError("recommended_action must match the top-ranked evaluation.")
        ranks = [ranked.rank for ranked in self.ranked_actions]
        expected = list(range(1, len(self.ranked_actions) + 1))
        if ranks != expected:
            raise ValueError(
                f"ranked_actions ranks must be contiguous from 1. Got {ranks}, expected {expected}."
            )


@dataclass(frozen=True)
class EvaluatorConfig:
    """Configuration for Monte Carlo action evaluation."""

    n_samples: int
    seed: int

    def __post_init__(self) -> None:
        if self.n_samples < 1:
            raise ValueError(f"n_samples must be >= 1, got {self.n_samples}.")


@dataclass(frozen=True)
class _SampleOutcome:
    score: int
    taker_won: bool
    rollout: RolloutResult
    hidden_world_weight: float



def evaluate_actions(
    game_state: GameState,
    *,
    config: EvaluatorConfig,
    candidate_actions: tuple[PlayAction, ...] | None = None,
    belief_state: BeliefState | None = None,
    policies_by_player: tuple[TurnPolicy, ...] | None = None,
) -> tuple[ActionEvaluation, ...]:
    """Evaluate legal actions by sampling compatible worlds and rolling them out."""
    if game_state.next_player_index != game_state.context.player_index:
        raise ValueError("evaluate_actions is only defined when the observed player is next to act.")

    if candidate_actions is None:
        candidate_actions = legal_actions(game_state)
    if not candidate_actions:
        raise ValueError("candidate_actions must not be empty.")
    if belief_state is None:
        belief_state = build_belief_state(game_state)

    n_players = len(belief_state.remaining_card_counts_by_player)
    if policies_by_player is None:
        policies_by_player = tuple(HeuristicTurnPolicy() for _ in range(n_players))
    if len(policies_by_player) != n_players:
        raise ValueError(
            f"policies_by_player must contain exactly {n_players} policies, got {len(policies_by_player)}."
        )

    evaluations: list[ActionEvaluation] = []
    for action in candidate_actions:
        outcomes = [
            _evaluate_action_on_sample(
                game_state=game_state,
                action=action,
                belief_state=belief_state,
                sample_seed=config.seed + sample_index,
                policies_by_player=policies_by_player,
            )
            for sample_index in range(config.n_samples)
        ]
        evaluations.append(_aggregate_action_outcomes(action, outcomes))
    return tuple(evaluations)



def _evaluate_action_on_sample(
    *,
    game_state: GameState,
    action: PlayAction,
    belief_state: BeliefState,
    sample_seed: int,
    policies_by_player: tuple[TurnPolicy, ...],
) -> _SampleOutcome:
    rng = make_rng(sample_seed)
    weighted_sample = sample_weighted_world(game_state, rng=rng, belief_state=belief_state)
    next_world, _ = apply_play_action_world(weighted_sample.world_state, action)
    rollout = rollout_world(next_world, policies_by_player=policies_by_player)
    return _SampleOutcome(
        score=rollout.score.score,
        taker_won=rollout.score.taker_won,
        rollout=rollout,
        hidden_world_weight=weighted_sample.likelihood.weight,
    )



def _aggregate_action_outcomes(
    action: PlayAction, outcomes: list[_SampleOutcome]
) -> ActionEvaluation:
    scores = sorted(outcome.score for outcome in outcomes)
    wins = [outcome.taker_won for outcome in outcomes]
    expected_score = mean(scores)
    score_q10 = _quantile(scores, 0.10)
    robust_score = score_q10
    downside_risk = max(0.0, expected_score - robust_score)
    return ActionEvaluation(
        action=action,
        n_samples=len(outcomes),
        win_rate=sum(1 for won in wins if won) / len(wins),
        expected_score=expected_score,
        robust_score=robust_score,
        downside_risk=downside_risk,
        score_std=pstdev(scores),
        score_min=scores[0],
        score_max=scores[-1],
        score_q05=_quantile(scores, 0.05),
        score_q10=score_q10,
        score_q50=_quantile(scores, 0.50),
        score_q90=_quantile(scores, 0.90),
        score_q95=_quantile(scores, 0.95),
    )



def _quantile(sorted_scores: list[int], q: float) -> float:
    if len(sorted_scores) == 1:
        return float(sorted_scores[0])
    position = (len(sorted_scores) - 1) * q
    low = int(position)
    high = min(low + 1, len(sorted_scores) - 1)
    weight = position - low
    return sorted_scores[low] * (1.0 - weight) + sorted_scores[high] * weight
