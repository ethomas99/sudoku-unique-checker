"""Tests for the puzzle generator. Run with `pytest`."""

import random

from sudoku_unique.generator import count_clues, generate_full_board, generate_puzzle
from sudoku_unique.solver import BOARD_SIZE, EMPTY, count_solutions, find_conflicts


def test_generate_full_board_has_no_conflicts():
    grid = generate_full_board(random.Random(1))
    assert find_conflicts(grid) == []


def test_generate_full_board_has_no_empty_cells():
    grid = generate_full_board(random.Random(1))
    assert all(cell != EMPTY for row in grid for cell in row)


def test_generate_full_board_is_a_valid_completion():
    grid = generate_full_board(random.Random(2))
    solutions = count_solutions([row[:] for row in grid], limit=2)
    assert len(solutions) == 1


def test_generate_full_board_varies_with_seed():
    first = generate_full_board(random.Random(1))
    second = generate_full_board(random.Random(2))
    assert first != second


def test_generate_puzzle_has_unique_solution():
    grid = generate_puzzle(rng=random.Random(3))
    solutions = count_solutions([row[:] for row in grid], limit=2)
    assert len(solutions) == 1


def test_generate_puzzle_has_no_conflicts():
    grid = generate_puzzle(rng=random.Random(3))
    assert find_conflicts(grid) == []


def test_generate_puzzle_default_removes_more_than_clue_target():
    grid = generate_puzzle(rng=random.Random(4))
    assert count_clues(grid) < BOARD_SIZE * BOARD_SIZE


def test_generate_puzzle_respects_clue_target_as_a_floor():
    grid = generate_puzzle(clues=40, rng=random.Random(5))
    assert count_clues(grid) >= 40


def test_generate_puzzle_high_clue_target_is_met_exactly():
    # A generous target like 60 is always reachable -- digging stops the
    # moment the count hits it, long before the board could become minimal.
    grid = generate_puzzle(clues=60, rng=random.Random(6))
    assert count_clues(grid) == 60


def test_generate_puzzle_same_seed_is_deterministic():
    first = generate_puzzle(clues=40, rng=random.Random(7))
    second = generate_puzzle(clues=40, rng=random.Random(7))
    assert first == second
