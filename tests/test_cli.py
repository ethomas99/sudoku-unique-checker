"""Tests for the CLI layer. Run with `pytest`."""

import json

from sudoku_unique.cli import build_result, main, split_boards

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


def test_split_boards_single_line_is_one_board():
    assert split_boards(SOLVED_BOARD) == [SOLVED_BOARD]


def test_split_boards_nine_line_grid_is_one_board():
    grid_text = "\n".join(SOLVED_BOARD[i : i + 9] for i in range(0, 81, 9))
    assert split_boards(grid_text) == [grid_text]


def test_split_boards_multiple_lines_are_separate_boards():
    text = "\n".join([SOLVED_BOARD, "." * 81, "11" + "." * 79])
    assert split_boards(text) == [SOLVED_BOARD, "." * 81, "11" + "." * 79]


def test_split_boards_ignores_blank_lines_between_boards():
    text = f"{SOLVED_BOARD}\n\n{'.' * 81}\n"
    assert split_boards(text) == [SOLVED_BOARD, "." * 81]


def test_main_reads_multiple_boards_from_file(tmp_path, capsys):
    path = tmp_path / "boards.txt"
    path.write_text(f"{SOLVED_BOARD}\n{'.' * 81}\n")

    exit_code = main(["--json", str(path)])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 2
    assert out[0]["unique"] is True
    assert out[1]["unique"] is False


def test_main_multiple_boards_human_output_is_labeled(tmp_path, capsys):
    path = tmp_path / "boards.txt"
    path.write_text(f"{SOLVED_BOARD}\n11{'.' * 79}\n")

    exit_code = main([str(path)])
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "board 1:" in out
    assert "board 2:" in out
    assert "invalid board" in out
