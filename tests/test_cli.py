"""Tests for the CLI layer. Run with `pytest`."""

import json

import pytest

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


def test_build_result_without_difficulty_flag_omits_field():
    result = build_result("." + SOLVED_BOARD[1:])
    assert "difficulty" not in result


def test_build_result_difficulty_reports_easy_for_forced_board():
    result = build_result("." + SOLVED_BOARD[1:], with_difficulty=True)
    assert result["difficulty"] == "easy"


def test_build_result_difficulty_is_none_for_non_unique_board():
    result = build_result("." * 81, with_difficulty=True)
    assert result["difficulty"] is None


def test_build_result_difficulty_is_none_for_invalid_board():
    result = build_result("11" + "." * 79, with_difficulty=True)
    assert result["difficulty"] is None


def test_main_difficulty_flag_included_in_json_output(capsys):
    exit_code = main(["--json", "--difficulty", "." + SOLVED_BOARD[1:]])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["difficulty"] == "easy"


def test_main_difficulty_flag_printed_in_human_output(capsys):
    exit_code = main(["--difficulty", "." + SOLVED_BOARD[1:]])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "difficulty: easy" in out


def test_main_generate_prints_a_unique_board(capsys):
    exit_code = main(["--generate", "--seed", "42"])
    assert exit_code == 0
    out = capsys.readouterr().out.strip()
    lines = out.splitlines()
    assert len(lines) == 9
    assert all(len(line) == 9 for line in lines)

    result = build_result(out)
    assert result["valid"] is True
    assert result["unique"] is True


def test_main_generate_json_mode(capsys):
    exit_code = main(["--generate", "--seed", "42", "--json"])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["board"]) == 81


def test_main_generate_same_seed_is_deterministic(capsys):
    main(["--generate", "--seed", "7"])
    first = capsys.readouterr().out
    main(["--generate", "--seed", "7"])
    second = capsys.readouterr().out
    assert first == second


def test_main_generate_rejects_board_argument(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--generate", "." * 81])
    assert excinfo.value.code == 2


def test_main_generate_respects_clues_target(capsys):
    exit_code = main(["--generate", "--seed", "1", "--clues", "40", "--json"])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["board"].count(".") <= 41


def test_main_requires_board_without_generate(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_main_multiple_boards_human_output_is_labeled(tmp_path, capsys):
    path = tmp_path / "boards.txt"
    path.write_text(f"{SOLVED_BOARD}\n11{'.' * 79}\n")

    exit_code = main([str(path)])
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "board 1:" in out
    assert "board 2:" in out
    assert "invalid board" in out
