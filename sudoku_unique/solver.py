"""Parse and solve Sudoku boards, with one goal: count solutions accurately.

Puzzle setters care about a single question -- does this board have exactly
one solution? -- more than they care about seeing any particular solution.
A board with two solutions isn't a real puzzle, no matter how nice the first
solution a naive solver finds looks. Everything here is built around
answering that question quickly.
"""

from __future__ import annotations

BOARD_SIZE = 9
BOX_SIZE = 3
EMPTY = 0


class InvalidBoard(ValueError):
    """Raised when a board string can't be parsed into a 9x9 grid."""


def parse_board(text: str) -> list[list[int]]:
    """Parse an 81-character board string into a 9x9 grid of ints (0 = empty).

    Accepts '.', '0', or whitespace as empty-cell markers. Whitespace in the
    input is stripped before parsing, so a single 81-char line and a 9-line
    grid both work.
    """
    cleaned = "".join(ch for ch in text if not ch.isspace())
    if len(cleaned) != BOARD_SIZE * BOARD_SIZE:
        raise InvalidBoard(
            f"expected {BOARD_SIZE * BOARD_SIZE} board cells, got {len(cleaned)}"
        )

    grid: list[list[int]] = []
    for row in range(BOARD_SIZE):
        row_cells: list[int] = []
        for col in range(BOARD_SIZE):
            ch = cleaned[row * BOARD_SIZE + col]
            if ch in ".0":
                row_cells.append(EMPTY)
            elif ch.isdigit():
                row_cells.append(int(ch))
            else:
                pos = row * BOARD_SIZE + col
                raise InvalidBoard(f"unexpected character {ch!r} at position {pos}")
        grid.append(row_cells)
    return grid


def find_conflicts(grid: list[list[int]]) -> list[str]:
    """Return human-readable rule violations already present on the board.

    This runs before solving: a board with a duplicate digit in a row,
    column, or box has zero solutions by definition, and it's worth telling
    the caller exactly where the problem is rather than just reporting
    "no solution".
    """
    conflicts: list[str] = []

    for row in range(BOARD_SIZE):
        seen: dict[int, int] = {}
        for col in range(BOARD_SIZE):
            value = grid[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                conflicts.append(
                    f"row {row + 1} has duplicate {value} at columns "
                    f"{seen[value] + 1} and {col + 1}"
                )
            else:
                seen[value] = col

    for col in range(BOARD_SIZE):
        seen = {}
        for row in range(BOARD_SIZE):
            value = grid[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                conflicts.append(
                    f"column {col + 1} has duplicate {value} at rows "
                    f"{seen[value] + 1} and {row + 1}"
                )
            else:
                seen[value] = row

    for box_row in range(0, BOARD_SIZE, BOX_SIZE):
        for box_col in range(0, BOARD_SIZE, BOX_SIZE):
            seen = {}
            for r in range(box_row, box_row + BOX_SIZE):
                for c in range(box_col, box_col + BOX_SIZE):
                    value = grid[r][c]
                    if value == EMPTY:
                        continue
                    if value in seen:
                        conflicts.append(
                            f"3x3 box at row {box_row + 1}, column {box_col + 1} "
                            f"has duplicate {value}"
                        )
                    else:
                        seen[value] = (r, c)

    return conflicts


def _candidates(grid: list[list[int]], row: int, col: int) -> list[int]:
    used = set(grid[row])
    used.update(grid[r][col] for r in range(BOARD_SIZE))
    box_row, box_col = (row // BOX_SIZE) * BOX_SIZE, (col // BOX_SIZE) * BOX_SIZE
    for r in range(box_row, box_row + BOX_SIZE):
        for c in range(box_col, box_col + BOX_SIZE):
            used.add(grid[r][c])
    return [v for v in range(1, 10) if v not in used]


def count_solutions(grid: list[list[int]], limit: int = 2) -> list[list[list[int]]]:
    """Count solutions up to `limit`, stopping the search as soon as it's hit.

    An empty board has over 6 billion solutions, so exhaustively finding
    them all would be pointless -- uniqueness only needs to distinguish
    "zero", "one", and "more than one". The default limit of 2 is exactly
    what's needed for that, and picking the emptiest cell first (rather than
    scanning in row order) keeps the search fast on real puzzles.
    """
    solutions: list[list[list[int]]] = []

    def solve() -> None:
        if len(solutions) >= limit:
            return

        best_cell = None
        best_candidates: list[int] | None = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if grid[row][col] != EMPTY:
                    continue
                cands = _candidates(grid, row, col)
                if not cands:
                    return
                if best_candidates is None or len(cands) < len(best_candidates):
                    best_cell, best_candidates = (row, col), cands
                    if len(cands) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            solutions.append([row[:] for row in grid])
            return

        row, col = best_cell
        for value in best_candidates:
            grid[row][col] = value
            solve()
            grid[row][col] = EMPTY
            if len(solutions) >= limit:
                return

    solve()
    return solutions


def format_board(grid: list[list[int]]) -> str:
    return "\n".join("".join(str(v) if v else "." for v in row) for row in grid)
