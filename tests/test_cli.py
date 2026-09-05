"""Tests for the CLI layer. Run with `pytest`."""

import json

from sudoku_unique.cli import build_result, main

SOLVED_BOARD = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)


def test_build_result_unique_solution():
    result = build_result("." + SOLVED_BOARD[1:])
    assert result["valid"] is True
    assert result["solution_count"] == 1
    assert result["unique"] is True
    assert result["solution"] == "\n".join(
        SOLVED_BOARD[i : i + 9] for i in range(0, 81, 9)
    )


def test_build_result_multiple_solutions():
    result = build_result("." * 81)
    assert result["valid"] is True
    assert result["solution_count"] == 2
    assert result["unique"] is False
    assert result["solution"] is None


def test_build_result_invalid_board_reports_conflicts():
    result = build_result("11" + "." * 79)
    assert result["valid"] is False
    assert result["unique"] is False
    assert result["solution_count"] == 0
    assert len(result["conflicts"]) == 1


def test_main_json_mode_prints_valid_json(capsys):
    exit_code = main(["--json", "." + SOLVED_BOARD[1:]])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["unique"] is True


def test_main_reads_board_argument_directly(capsys):
    exit_code = main(["11" + "." * 79])
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "invalid board" in out


def test_main_bad_length_returns_error(capsys):
    exit_code = main(["--json", "123"])
    assert exit_code == 1
    out = json.loads(capsys.readouterr().out)
    assert out["valid"] is False
    assert "error" in out
