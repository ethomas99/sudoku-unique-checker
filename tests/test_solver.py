"""Tests for the solver. Run with `pytest`."""

import pytest

from sudoku_unique.solver import (
    BOARD_SIZE,
    EMPTY,
    InvalidBoard,
    count_solutions,
    find_conflicts,
    format_board,
    parse_board,
)

# A verified complete Sudoku grid (Wikipedia's canonical example solution).
# Every row, column, and 3x3 box is a permutation of 1-9.
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

BLANK_BOARD = "." * 81


def test_parse_board_accepts_dots_and_zeros():
    grid = parse_board("0" * 40 + "." * 41)
    assert len(grid) == BOARD_SIZE
    assert all(len(row) == BOARD_SIZE for row in grid)
    assert all(cell == EMPTY for row in grid for cell in row)


def test_parse_board_strips_whitespace_and_newlines():
    text = "\n".join(SOLVED_BOARD[i : i + 9] for i in range(0, 81, 9))
    grid = parse_board(text)
    assert "".join(str(v) for row in grid for v in row) == SOLVED_BOARD


def test_parse_board_wrong_length_raises():
    with pytest.raises(InvalidBoard):
        parse_board("123")


def test_parse_board_bad_character_raises():
    with pytest.raises(InvalidBoard):
        parse_board("x" * 81)


def test_find_conflicts_none_on_valid_board():
    grid = parse_board(SOLVED_BOARD)
    assert find_conflicts(grid) == []


def test_find_conflicts_detects_row_duplicate():
    grid = parse_board("11" + "." * 79)
    conflicts = find_conflicts(grid)
    assert len(conflicts) == 1
    assert "row 1" in conflicts[0]


def test_find_conflicts_detects_column_duplicate():
    grid = parse_board(BLANK_BOARD)
    grid[0][0] = 5
    grid[1][0] = 5
    conflicts = find_conflicts(grid)
    assert len(conflicts) == 1
    assert "column 1" in conflicts[0]


def test_find_conflicts_detects_box_duplicate():
    grid = parse_board(BLANK_BOARD)
    grid[0][0] = 7
    grid[1][1] = 7
    conflicts = find_conflicts(grid)
    assert len(conflicts) == 1
    assert "box" in conflicts[0]


def test_count_solutions_already_solved_board_has_one_solution():
    grid = parse_board(SOLVED_BOARD)
    solutions = count_solutions(grid)
    assert len(solutions) == 1
    assert "".join(str(v) for row in solutions[0] for v in row) == SOLVED_BOARD


def test_count_solutions_single_blank_cell_is_forced():
    # Blanking one cell of a complete grid always has exactly one
    # completion: its row, column, and box already contain the other
    # eight digits between them, so only the missing digit fits.
    grid = parse_board("." + SOLVED_BOARD[1:])
    solutions = count_solutions(grid)
    assert len(solutions) == 1
    assert "".join(str(v) for row in solutions[0] for v in row) == SOLVED_BOARD


def test_count_solutions_two_blank_cells_each_forced_by_column():
    # Row 9 is "345286179". Blank its first two cells (3 and 4). The row
    # alone would allow either order, but column 1 already holds a 4 (row
    # 5) and column 2 already holds a 3 (row 1), so each blank cell has
    # exactly one legal candidate once its column is taken into account,
    # with no backtracking needed.
    grid = parse_board(SOLVED_BOARD[:72] + ".." + SOLVED_BOARD[74:])
    solutions = count_solutions(grid)
    assert len(solutions) == 1
    assert "".join(str(v) for row in solutions[0] for v in row) == SOLVED_BOARD


def test_count_solutions_blank_board_has_multiple():
    grid = parse_board(BLANK_BOARD)
    solutions = count_solutions(grid, limit=2)
    assert len(solutions) == 2


def test_count_solutions_respects_limit():
    grid = parse_board(BLANK_BOARD)
    solutions = count_solutions(grid, limit=1)
    assert len(solutions) == 1


def test_count_solutions_unsolvable_board_has_none():
    # Row 0 fills every digit but 9, which forces cell (0, 8) to be 9 by
    # row elimination. The top-right box already holds a 9 at (1, 6), so
    # that cell ends up with zero legal candidates. No row/column/box rule
    # is broken outright -- the box holds three distinct values -- so
    # find_conflicts sees nothing wrong; only the solver discovers the
    # contradiction.
    grid = parse_board(BLANK_BOARD)
    for col in range(8):
        grid[0][col] = col + 1
    grid[1][6] = 9
    assert find_conflicts(grid) == []
    solutions = count_solutions(grid)
    assert len(solutions) == 0


def test_format_board_uses_dot_for_empty():
    grid = parse_board(BLANK_BOARD)
    assert format_board(grid) == "\n".join(["." * 9] * 9)
