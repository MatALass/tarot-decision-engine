"""CLI integration tests using Typer's test runner."""

import json

from typer.testing import CliRunner

from tarot_engine.cli.main import app
from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import generate_deck
from tarot_engine.domain.enums import Contract
from tarot_engine.utils.parsing import format_card_token

runner = CliRunner()


def _hand_str() -> str:
    deck = generate_deck()
    bouts = [Card.excuse(), Card.trump(1), Card.trump(21)]
    fillers = [c for c in deck if not c.is_bout][:12]
    return ",".join(str(c) for c in bouts + fillers)


def _move_base() -> list[str]:
    deck = generate_deck()
    remaining = ",".join(format_card_token(card) for card in (deck[13], deck[14]))
    other_cards = iter(deck[15:])
    args = [
        "recommend-move",
        "--remaining-hand", remaining,
        "--contract", "GARDE",
        "--player-index", "0",
        "--taker-index", "0",
    ]
    for trick_index in range(13):
        entries = [f"0:{format_card_token(deck[trick_index])}"]
        for player_index in range(1, 5):
            entries.append(f"{player_index}:{format_card_token(next(other_cards))}")
        args.extend(["--completed-trick", "|".join(entries)])
    args.extend([
        "--current-trick", f"4:{format_card_token(next(other_cards))}",
        "--next-player-index", "0",
        "--n-samples", "5",
        "--seed", "7",
    ])
    return args


HAND = _hand_str()
BASE = ["evaluate-hand", "--hand", HAND, "--n-simulations", "20", "--seed", "42"]
MOVE_BASE = _move_base()


class TestEvaluateHandBasic:
    def test_exits_zero(self) -> None:
        assert runner.invoke(app, BASE).exit_code == 0

    def test_output_contains_contract_names(self) -> None:
        out = runner.invoke(app, BASE).output
        assert "PRISE" in out and "GARDE" in out

    def test_output_contains_win_rate_percent(self) -> None:
        assert "%" in runner.invoke(app, BASE).output

    def test_reproducible_output(self) -> None:
        assert runner.invoke(app, BASE).output == runner.invoke(app, BASE).output


class TestJsonOutput:
    def test_valid_json(self) -> None:
        result = runner.invoke(app, BASE + ["--output", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_required_keys(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--output", "json"]).output)
        for key in ("recommended_contract", "policy_name", "rationale", "warnings", "contracts"):
            assert key in data

    def test_recommended_contract_valid(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--output", "json"]).output)
        assert data["recommended_contract"] in {c.value for c in Contract}

    def test_four_contracts_by_default(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--output", "json"]).output)
        assert len(data["contracts"]) == 4

    def test_win_rates_in_range(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--output", "json"]).output)
        for entry in data["contracts"]:
            assert 0.0 <= entry["win_rate"] <= 1.0

    def test_ranks_contiguous(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--output", "json"]).output)
        ranks = [e["rank"] for e in data["contracts"]]
        assert ranks == list(range(1, len(ranks) + 1))


class TestContractFiltering:
    def test_single_contract(self) -> None:
        result = runner.invoke(app, BASE + ["--contracts", "PRISE", "--output", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["contracts"]) == 1
        assert data["contracts"][0]["contract"] == "PRISE"

    def test_two_contracts(self) -> None:
        result = runner.invoke(app, BASE + [
            "--contracts", "PRISE", "--contracts", "GARDE", "--output", "json"
        ])
        names = {e["contract"] for e in json.loads(result.output)["contracts"]}
        assert names == {"PRISE", "GARDE"}

    def test_invalid_contract_exits_nonzero(self) -> None:
        assert runner.invoke(app, BASE + ["--contracts", "GROS_CHELEM"]).exit_code != 0


class TestPolicies:
    def test_conservative(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--policy", "conservative", "--output", "json"]).output)
        assert data["policy_name"] == "conservative"

    def test_expected_value(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--policy", "expected_value", "--output", "json"]).output)
        assert data["policy_name"] == "expected_value"

    def test_balanced(self) -> None:
        data = json.loads(runner.invoke(app, BASE + ["--policy", "balanced", "--output", "json"]).output)
        assert "balanced" in data["policy_name"]

    def test_balanced_risk_weight(self) -> None:
        data = json.loads(runner.invoke(app, BASE + [
            "--policy", "balanced", "--risk-weight", "1.5", "--output", "json"
        ]).output)
        assert "1.5" in data["policy_name"]


class TestMoveRecommendation:
    def test_exits_zero(self) -> None:
        assert runner.invoke(app, MOVE_BASE).exit_code == 0

    def test_output_contains_recommended_card(self) -> None:
        out = runner.invoke(app, MOVE_BASE).output
        assert "Recommended card" in out

    def test_json_output_valid(self) -> None:
        result = runner.invoke(app, MOVE_BASE + ["--output", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommended_action" in data
        assert "actions" in data

    def test_json_recommended_action_player_matches(self) -> None:
        data = json.loads(runner.invoke(app, MOVE_BASE + ["--output", "json"]).output)
        assert data["recommended_action"]["player_index"] == 0


class TestErrorHandling:
    def test_invalid_card_exits_nonzero(self) -> None:
        result = runner.invoke(app, [
            "evaluate-hand", "--hand", "INVALID,KH,T21",
            "--n-simulations", "5", "--seed", "0",
        ])
        assert result.exit_code != 0

    def test_wrong_hand_size_exits_nonzero(self) -> None:
        result = runner.invoke(app, [
            "evaluate-hand", "--hand", "T21,KH,EXCUSE",
            "--n-simulations", "5", "--seed", "0",
        ])
        assert result.exit_code != 0

    def test_invalid_completed_trick_exits_nonzero(self) -> None:
        result = runner.invoke(app, [
            "recommend-move",
            "--remaining-hand", "T1,KH",
            "--contract", "GARDE",
            "--player-index", "0",
            "--taker-index", "0",
            "--completed-trick", "0:T21|1:T20",
            "--next-player-index", "0",
        ])
        assert result.exit_code != 0
