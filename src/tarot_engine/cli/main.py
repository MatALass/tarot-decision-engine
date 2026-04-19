"""CLI entry point for the Tarot Decision Engine.

Usage examples
--------------
  tarot-engine evaluate-hand --hand "T21,T20,T18,EXCUSE,T1,KH,QH,VH,10H,AS,KS,QS,VS,10S,9S"
  tarot-engine evaluate-hand --hand "..." --contracts PRISE --contracts GARDE
  tarot-engine evaluate-hand --hand "..." --policy expected_value --n-simulations 2000 --seed 42
  tarot-engine evaluate-hand --hand "..." --policy balanced --risk-weight 1.0
  tarot-engine evaluate-hand --hand "..." --output json --seed 42
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Annotated, Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tarot_engine.application.dto import EvaluationRequest, EvaluationResponse
from tarot_engine.application.services import evaluate_hand
from tarot_engine.domain.enums import Contract

# ---------------------------------------------------------------------------
# App structure: one root Typer + one sub-Typer per command group.
# This pattern guarantees real subcommand dispatch in the shell regardless
# of how many commands are registered, and is compatible with Typer ≥ 0.9.
# ---------------------------------------------------------------------------

# Sub-app for the evaluate-hand command group.
_evaluate_app = typer.Typer(
    help="Evaluate a player hand using Monte Carlo simulation.",
    add_completion=False,
)

# Root app — dispatches to sub-apps.
app = typer.Typer(
    name="tarot-engine",
    help="Monte Carlo decision engine for 5-player French Tarot.",
    add_completion=False,
    no_args_is_help=True,
)
app.add_typer(_evaluate_app, name="evaluate-hand")

console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


class PolicyName(str, Enum):
    conservative   = "conservative"
    expected_value = "expected_value"
    balanced       = "balanced"


# ---------------------------------------------------------------------------
# evaluate-hand command
# ---------------------------------------------------------------------------

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
        _render_json(response)
    else:
        _render_text(response)


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


def _render_text(response: EvaluationResponse) -> None:
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
    table.add_column("Rank",        justify="center", width=6)
    table.add_column("Contract",    justify="left",   width=14)
    table.add_column("Win rate",    justify="right",  width=10)
    table.add_column("Exp. score",  justify="right",  width=12)
    table.add_column("Std",         justify="right",  width=8)
    table.add_column("Q10",         justify="right",  width=8)
    table.add_column("Median",      justify="right",  width=8)
    table.add_column("Q90",         justify="right",  width=8)
    table.add_column("Simulations", justify="right",  width=12)
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


def _render_json(response: EvaluationResponse) -> None:
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
