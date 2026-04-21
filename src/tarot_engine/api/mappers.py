"""Mapping helpers from internal application responses to HTTP schemas."""

from __future__ import annotations

from tarot_engine.api.schemas import (
    ApiActionEvaluationItem,
    ApiActionReference,
    ApiContractEvaluationItem,
    ApiContractEvaluationResponse,
    ApiContractRecommendationItem,
    ApiMoveEvaluationResponse,
    ApiMoveExplanation,
    ApiRankedActionItem,
)
from tarot_engine.application.dto import EvaluationResponse, MoveEvaluationResponse
from tarot_engine.utils.parsing import format_card_token


def to_api_contract_response(response: EvaluationResponse) -> ApiContractEvaluationResponse:
    recommendation = response.recommendation
    return ApiContractEvaluationResponse(
        recommended_contract=recommendation.recommended_contract.value,
        policy_name=recommendation.policy_name,
        rationale=recommendation.rationale,
        warnings=list(recommendation.warnings),
        ranked_contracts=[
            ApiContractRecommendationItem(
                rank=item.rank,
                contract=item.contract.value,
                expected_score=item.evaluation.expected_score,
                win_rate=item.evaluation.win_rate,
            )
            for item in recommendation.ranked_contracts
        ],
        evaluations=[
            ApiContractEvaluationItem(
                contract=item.contract.value,
                win_rate=item.win_rate,
                expected_score=item.expected_score,
                score_std=item.score_std,
                score_q10=item.score_q10,
                score_q50=item.score_q50,
                score_q90=item.score_q90,
                n_simulations=item.n_simulations,
            )
            for item in response.evaluations
        ],
    )


def to_api_move_response(response: MoveEvaluationResponse) -> ApiMoveEvaluationResponse:
    recommendation = response.recommendation
    explanation = response.explanation
    return ApiMoveEvaluationResponse(
        recommended_action=ApiActionReference(
            player_index=recommendation.recommended_action.player_index,
            card=format_card_token(recommendation.recommended_action.card),
        ),
        policy_name=recommendation.policy_name,
        rationale=recommendation.rationale,
        warnings=[],
        ranked_actions=[
            ApiRankedActionItem(
                rank=item.rank,
                action=ApiActionReference(
                    player_index=item.evaluation.action.player_index,
                    card=format_card_token(item.evaluation.action.card),
                ),
                expected_score=item.evaluation.expected_score,
                win_rate=item.evaluation.win_rate,
            )
            for item in recommendation.ranked_actions
        ],
        evaluations=[
            ApiActionEvaluationItem(
                action=ApiActionReference(
                    player_index=item.action.player_index,
                    card=format_card_token(item.action.card),
                ),
                expected_score=item.expected_score,
                win_rate=item.win_rate,
                score_std=item.score_std,
                score_q10=item.score_q10,
                score_q50=item.score_q50,
                score_q90=item.score_q90,
                n_samples=item.n_samples,
            )
            for item in response.evaluations
        ],
        explanation=ApiMoveExplanation(
            summary=explanation.summary,
            top_gap_expected_score=explanation.top_gap_expected_score,
            top_gap_win_rate=explanation.top_gap_win_rate,
            risk_comment=explanation.risk_comment,
            alternatives_summary=list(explanation.alternatives_summary),
        ),
    )
