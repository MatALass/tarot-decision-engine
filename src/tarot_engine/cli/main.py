"""CLI entry point for the Tarot Decision Engine."""

from __future__ import annotations

import json
from enum import Enum
from typing import Annotated, Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tarot_engine.application.dto import (
    EvaluationRequest,
    EvaluationResponse,
    MoveEvaluationRequest,
    MoveEvaluationResponse,
)
from tarot_engine.application.services import evaluate_hand, evaluate_move
from tarot_engine.domain.enums import Contract
from tarot_engine.utils.parsing import format_card_token

_evaluate_app = typer.Typer(
    help="Evaluate a player hand using Monte Carlo simulation.",
    add_completion=False,
)
_move_app = typer.Typer(
    help="Recommend a move from an intermediate observable game state.",
    add_completion=False,
)

app = typer.Typer(
    name="tarot-engine",
    help="Monte Carlo decision engine for 5-player French Tarot.",
    add_completion=False,
    no_args_is_help=True,
)
app.add_typer(_evaluate_app, name="evaluate-hand")
app.add_typer(_move_app, name="recommend-move")

console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


class PolicyName(str, Enum):
    conservative = "conservative"
    expected_value = "expected_value"
    balanced = "balanced"


class MovePolicyName(str, Enum):
    expected_score = "expected_score"


@_evaluate_app.callback(invoke_without_command=True)
def evaluate_hand_cmd(
    hand: Annotated[str, typer.Option(
        "--hand", "-h",
        help="Comma-separated list of 15 card tokens (e.g. T21,KH,EXCUSE,10D,...).",
    )],
    contracts: Annotated[Optional[list[str]], typer.Option(
        "--contracts", "-c",
        help="Contracts to evaluate. Repeat for multiple. Defaults to all four.",
    )] = None,
    n_simulations: Annotated[int, typer.Option(
        "--n-simulations", "-n",
        help="Monte Carlo simulations per contract.",
        min=1,
        max=100_000,
    )] = 1_000,
    seed: Annotated[int, typer.Option(
        "--seed",
        help="RNG seed for reproducibility.",
    )] = 0,
    policy: Annotated[PolicyName, typer.Option(
        "--policy", "-p",
        help="Decision policy.",
        case_sensitive=False,
    )] = PolicyName.conservative,
    risk_weight: Annotated[float, typer.Option(
        "--risk-weight",
        help="Risk aversion weight for the balanced policy (≥ 0).",
        min=0.0,
    )] = 0.5,
    output: Annotated[OutputFormat, typer.Option(
        "--output", "-o",
        help="Output format: text | json.",
        case_sensitive=False,
    )] = OutputFormat.text,
) -> None:
    """Evaluate a 15-card Tarot hand and recommend the best contract."""
    parsed_contracts = _parse_contracts(contracts)
    try:
        request = EvaluationRequest(
            hand_str=hand,
            contracts=tuple(parsed_contracts),
            n_simulations=n_simulations,
            seed=seed,
            policy=policy.value,
            risk_weight=risk_weight,
        )
        response = evaluate_hand(request)
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    if output == OutputFormat.json:
        _render_contract_json(response)
    else:
        _render_contract_text(response)


@_move_app.callback(invoke_without_command=True)
def recommend_move_cmd(
    remaining_hand: Annotated[str, typer.Option(
        "--remaining-hand",
        help="Comma-separated remaining hand of the observed player.",
    )],
    contract: Annotated[str, typer.Option(
        "--contract",
        help="Current contract.",
    )],
    player_index: Annotated[int, typer.Option("--player-index", min=0, max=4)] = 0,
    taker_index: Annotated[int, typer.Option("--taker-index", min=0, max=4)] = 0,
    partner_index: Annotated[int | None, typer.Option("--partner-index", min=0, max=4)] = None,
    completed_trick: Annotated[Optional[list[str]], typer.Option(
        "--completed-trick",
        help="Completed trick in play order, format '0:T21|1:T20|2:KH|3:QH|4:EXCUSE'. Repeat for multiple tricks.",
    )] = None,
    current_trick: Annotated[str, typer.Option(
        "--current-trick",
        help="Current trick in play order, format '1:KH|2:QH'.",
    )] = "",
    next_player_index: Annotated[int, typer.Option("--next-player-index", min=0, max=4)] = 0,
    n_samples: Annotated[int, typer.Option("--n-samples", min=1, max=100_000)] = 200,
    seed: Annotated[int, typer.Option("--seed")] = 0,
    policy: Annotated[MovePolicyName, typer.Option(
        "--policy", case_sensitive=False, help="Move recommendation policy."
    )] = MovePolicyName.expected_score,
    output: Annotated[OutputFormat, typer.Option(
        "--output", "-o", help="Output format: text | json.", case_sensitive=False
    )] = OutputFormat.text,
) -> None:
    """Recommend a move from an intermediate observable state."""
    try:
        request = MoveEvaluationRequest(
            remaining_hand_str=remaining_hand,
            contract=_parse_contract(contract),
            player_index=player_index,
            taker_index=taker_index,
            partner_index=partner_index,
            completed_trick_strs=tuple(completed_trick or []),
            current_trick_str=current_trick,
            next_player_index=next_player_index,
            n_samples=n_samples,
            seed=seed,
            policy=policy.value,
        )
        response = evaluate_move(request)
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    if output == OutputFormat.json:
        _render_move_json(response)
    else:
        _render_move_text(response)


def _parse_contracts(raw: Optional[list[str]]) -> list[Contract]:
    if not raw:
        return list(Contract)
    valid = {c.value: c for c in Contract}
    result: list[Contract] = []
    errors: list[str] = []
    for name in raw:
        upper = name.strip().upper()
        if upper in valid:
            result.append(valid[upper])
        else:
            errors.append(name)
    if errors:
        err_console.print(
            f"[bold red]Error:[/bold red] Unknown contract(s): {', '.join(errors)}. "
            f"Valid: {', '.join(valid)}."
        )
        raise typer.Exit(code=1)
    seen: set[Contract] = set()
    deduped: list[Contract] = []
    for c in result:
        if c not in seen:
            deduped.append(c)
            seen.add(c)
    return deduped


def _parse_contract(raw: str) -> Contract:
    valid = {c.value: c for c in Contract}
    upper = raw.strip().upper()
    if upper not in valid:
        raise ValueError(
            f"Unknown contract '{raw}'. Valid options: {', '.join(valid)}."
        )
    return valid[upper]


def _render_contract_text(response: EvaluationResponse) -> None:
    rec = response.recommendation
    console.print()
    console.print(Panel(
        f"[bold green]Recommended: {rec.recommended_contract.value}[/bold green]\n"
        f"Policy: [cyan]{rec.policy_name}[/cyan]",
        title="[bold]Tarot Decision Engine[/bold]",
        border_style="green",
    ))
    console.print()
    console.print(f"[bold]Rationale:[/bold] {rec.rationale}")
    if rec.warnings:
        console.print()
        for w in rec.warnings:
            console.print(f"[bold yellow]⚠  {w}[/bold yellow]")
    console.print()
    table = Table(title="Contract Evaluations", box=box.ROUNDED,
                  show_header=True, header_style="bold cyan")
    table.add_column("Rank", justify="center", width=6)
    table.add_column("Contract", justify="left", width=14)
    table.add_column("Win rate", justify="right", width=10)
    table.add_column("Exp. score", justify="right", width=12)
    table.add_column("Std", justify="right", width=8)
    table.add_column("Q10", justify="right", width=8)
    table.add_column("Median", justify="right", width=8)
    table.add_column("Q90", justify="right", width=8)
    table.add_column("Simulations", justify="right", width=12)
    for rc in rec.ranked_contracts:
        ev = rc.evaluation
        table.add_row(
            str(rc.rank), ev.contract.value,
            f"{ev.win_rate:.1%}", f"{ev.expected_score:+.0f}",
            f"{ev.score_std:.0f}", f"{ev.score_q10:+.0f}",
            f"{ev.score_q50:+.0f}", f"{ev.score_q90:+.0f}",
            str(ev.n_simulations),
            style="bold green" if rc.rank == 1 else "",
        )
    console.print(table)
    console.print()


def _render_contract_json(response: EvaluationResponse) -> None:
    rec = response.recommendation
    payload = {
        "recommended_contract": rec.recommended_contract.value,
        "policy_name": rec.policy_name,
        "rationale": rec.rationale,
        "warnings": list(rec.warnings),
        "contracts": [
            {
                "rank": rc.rank,
                "contract": rc.evaluation.contract.value,
                "win_rate": round(rc.evaluation.win_rate, 4),
                "expected_score": round(rc.evaluation.expected_score, 2),
                "score_std": round(rc.evaluation.score_std, 2),
                "score_min": rc.evaluation.score_min,
                "score_max": rc.evaluation.score_max,
                "score_q10": round(rc.evaluation.score_q10, 2),
                "score_q50": round(rc.evaluation.score_q50, 2),
                "score_q90": round(rc.evaluation.score_q90, 2),
                "n_simulations": rc.evaluation.n_simulations,
            }
            for rc in rec.ranked_contracts
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _render_move_text(response: MoveEvaluationResponse) -> None:
    rec = response.recommendation
    explanation = response.explanation
    console.print()
    console.print(Panel(
        f"[bold green]Recommended card: {format_card_token(rec.recommended_action.card)}[/bold green]\n"
        f"Played by player: [cyan]{rec.recommended_action.player_index}[/cyan]\n"
        f"Policy: [cyan]{rec.policy_name}[/cyan]",
        title="[bold]Tarot Move Recommendation[/bold]",
        border_style="green",
    ))
    console.print()
    console.print(f"[bold]Rationale:[/bold] {rec.rationale}")
    console.print(f"[bold]Explanation:[/bold] {explanation.summary}")
    console.print(f"[bold]Risk:[/bold] {explanation.risk_comment}")
    if explanation.alternatives_summary:
        console.print("[bold]Alternatives:[/bold]")
        for line in explanation.alternatives_summary:
            console.print(f"  - {line}")
    console.print()
    table = Table(title="Move Evaluations", box=box.ROUNDED,
                  show_header=True, header_style="bold cyan")
    table.add_column("Rank", justify="center", width=6)
    table.add_column("Card", justify="left", width=10)
    table.add_column("Win rate", justify="right", width=10)
    table.add_column("Exp. score", justify="right", width=12)
    table.add_column("Std", justify="right", width=8)
    table.add_column("Q10", justify="right", width=8)
    table.add_column("Median", justify="right", width=8)
    table.add_column("Q90", justify="right", width=8)
    table.add_column("Samples", justify="right", width=10)
    for ranked in rec.ranked_actions:
        ev = ranked.evaluation
        table.add_row(
            str(ranked.rank), str(ev.action.card), f"{ev.win_rate:.1%}",
            f"{ev.expected_score:+.0f}", f"{ev.score_std:.0f}",
            f"{ev.score_q10:+.0f}", f"{ev.score_q50:+.0f}",
            f"{ev.score_q90:+.0f}", str(ev.n_samples),
            style="bold green" if ranked.rank == 1 else "",
        )
    console.print(table)
    console.print()


def _render_move_json(response: MoveEvaluationResponse) -> None:
    rec = response.recommendation
    explanation = response.explanation
    payload = {
        "recommended_action": {
            "player_index": rec.recommended_action.player_index,
            "card": format_card_token(rec.recommended_action.card),
        },
        "policy_name": rec.policy_name,
        "rationale": rec.rationale,
        "explanation": {
            "summary": explanation.summary,
            "top_gap_expected_score": round(explanation.top_gap_expected_score, 2),
            "top_gap_win_rate": round(explanation.top_gap_win_rate, 4),
            "risk_comment": explanation.risk_comment,
            "alternatives_summary": list(explanation.alternatives_summary),
        },
        "actions": [
            {
                "rank": ranked.rank,
                "player_index": ranked.evaluation.action.player_index,
                "card": format_card_token(ranked.evaluation.action.card),
                "win_rate": round(ranked.evaluation.win_rate, 4),
                "expected_score": round(ranked.evaluation.expected_score, 2),
                "score_std": round(ranked.evaluation.score_std, 2),
                "score_min": ranked.evaluation.score_min,
                "score_max": ranked.evaluation.score_max,
                "score_q10": round(ranked.evaluation.score_q10, 2),
                "score_q50": round(ranked.evaluation.score_q50, 2),
                "score_q90": round(ranked.evaluation.score_q90, 2),
                "n_samples": ranked.evaluation.n_samples,
            }
            for ranked in rec.ranked_actions
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
