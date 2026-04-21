"""FastAPI application exposing the Tarot Decision Engine to a web frontend."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from tarot_engine.api.mappers import to_api_contract_response, to_api_move_response
from tarot_engine.api.schemas import (
    ApiContractEvaluationRequest,
    ApiContractEvaluationResponse,
    ApiHealthResponse,
    ApiMoveEvaluationRequest,
    ApiMoveEvaluationResponse,
)
from tarot_engine.application.dto import EvaluationRequest, MoveEvaluationRequest
from tarot_engine.application.services import evaluate_hand, evaluate_move
from tarot_engine.domain.enums import Contract

app = FastAPI(
    title="Tarot Decision Engine API",
    version="0.1.0",
    description="HTTP API for contract evaluation and turn-by-turn move recommendation.",
)


@app.get("/api/v1/health", response_model=ApiHealthResponse)
def health() -> ApiHealthResponse:
    return ApiHealthResponse()


@app.get("/api/v1/meta/contracts", response_model=list[str])
def list_contracts() -> list[str]:
    return [contract.value for contract in Contract]


@app.post("/api/v1/contracts/evaluate", response_model=ApiContractEvaluationResponse)
def evaluate_contracts_endpoint(
    request: ApiContractEvaluationRequest,
) -> ApiContractEvaluationResponse:
    try:
        response = evaluate_hand(
            EvaluationRequest(
                hand_str=request.hand,
                contracts=tuple(_parse_contracts(request.contracts)),
                n_simulations=request.n_simulations,
                seed=request.seed,
                policy=request.policy,
                risk_weight=request.risk_weight,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return to_api_contract_response(response)


@app.post("/api/v1/moves/recommend", response_model=ApiMoveEvaluationResponse)
def recommend_move_endpoint(
    request: ApiMoveEvaluationRequest,
) -> ApiMoveEvaluationResponse:
    try:
        response = evaluate_move(
            MoveEvaluationRequest(
                remaining_hand_str=request.remaining_hand,
                contract=_parse_contract(request.contract),
                player_index=request.player_index,
                taker_index=request.taker_index,
                partner_index=request.partner_index,
                current_trick_str=request.current_trick,
                completed_trick_strs=tuple(request.completed_tricks),
                next_player_index=request.next_player_index,
                n_samples=request.n_samples,
                seed=request.seed,
                policy=request.policy,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return to_api_move_response(response)



def _parse_contract(value: str) -> Contract:
    normalized = value.strip().upper()
    for contract in Contract:
        if contract.value == normalized:
            return contract
    raise ValueError(
        f"Unknown contract '{value}'. Valid options: {', '.join(contract.value for contract in Contract)}."
    )



def _parse_contracts(values: list[str]) -> list[Contract]:
    if not values:
        return []
    return [_parse_contract(value) for value in values]
