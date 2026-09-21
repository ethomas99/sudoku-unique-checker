"""Generate random Sudoku puzzles with a guaranteed unique solution.

The approach is the standard two-step one: fill a full 9x9 grid at random,
then remove cells one at a time (in random order), keeping each removal
only if the board still has exactly one solution afterward. That's the
same uniqueness check the rest of this package is built around, so a
generated puzzle is checked the same way a hand-built one would be.
"""

from __future__ import annotations

import random

from .solver import BOARD_SIZE, EMPTY, _candidates, count_solutions


def generate_full_board(rng: random.Random | None = None) -> list[list[int]]:
    """Return a randomly filled, fully solved 9x9 grid.

    Fills the most-constrained empty cell first with its candidates in
    random order, same as the solver's search but keeping only the first
    completion found. That ordering makes dead ends rare enough that this
    finishes quickly without needing to retry from scratch on failure.
    """
    rng = rng or random.Random()
    grid = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def fill() -> bool:
        best_cell = None
        best_candidates: list[int] | None = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if grid[row][col] != EMPTY:
                    continue
                cands = _candidates(grid, row, col)
                if not cands:
                    return False
                if best_candidates is None or len(cands) < len(best_candidates):
                    best_cell, best_candidates = (row, col), cands
                    if len(cands) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            return True

        row, col = best_cell
        candidates = best_candidates[:]
        rng.shuffle(candidates)
        for value in candidates:
            grid[row][col] = value
            if fill():
                return True
            grid[row][col] = EMPTY
        return False

    fill()
    return grid


def count_clues(grid: list[list[int]]) -> int:
    return sum(1 for row in grid for cell in row if cell != EMPTY)


def generate_puzzle(
    clues: int | None = None, rng: random.Random | None = None
) -> list[list[int]]:
    """Generate a puzzle with a unique solution by digging holes in a full grid.

    Cells are blanked in random order, one at a time, each kept blank only
    if the board still has exactly one solution without it. If `clues` is
    given, digging stops as soon as that many clues remain; otherwise it
    keeps going until no single cell can be removed without breaking
    uniqueness, which produces a "minimal" puzzle. `clues` is a target, not
    a guarantee -- if the puzzle becomes minimal before reaching it, the
    result is left with more clues than asked for.
    """
    rng = rng or random.Random()
    grid = generate_full_board(rng)

    cells = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]
    rng.shuffle(cells)

    for row, col in cells:
        if clues is not None and count_clues(grid) <= clues:
            break

        removed = grid[row][col]
        grid[row][col] = EMPTY
        if len(count_solutions(grid, limit=2)) != 1:
            grid[row][col] = removed

    return grid
