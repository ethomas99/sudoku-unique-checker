"""Command-line entry point: does this Sudoku board have exactly one solution?"""

from __future__ import annotations

import argparse
import json
import random
import sys

from .generator import generate_puzzle
from .solver import (
    BOARD_SIZE,
    InvalidBoard,
    count_solutions,
    estimate_difficulty,
    find_conflicts,
    format_board,
    parse_board,
)


def _read_board_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    try:
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Not a path -- treat the argument itself as the board text.
        return source


def split_boards(text: str) -> list[str]:
    """Split input text into one or more board strings.

    A single board may be written as one 81-character line or wrapped
    across nine 9-character lines, and either form should still parse as
    one board. A file of several puzzles, on the other hand, is written
    one 81-character board per line. The two are told apart by shape: if
    every non-blank line is a full 81-cell board on its own, treat each
    line as a separate board; otherwise treat the whole text as a single
    board and let parse_board handle stripping newlines within it.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1 and all(len(line) == 81 for line in lines):
        return lines
    return [text]


def build_result(board_text: str, with_difficulty: bool = False) -> dict:
    grid = parse_board(board_text)
    conflicts = find_conflicts(grid)
    if conflicts:
        result = {
            "valid": False,
            "conflicts": conflicts,
            "solution_count": 0,
            "unique": False,
            "solution": None,
        }
        if with_difficulty:
            result["difficulty"] = None
        return result

    solutions = count_solutions(grid, limit=2)
    count = len(solutions)
    result = {
        "valid": True,
        "conflicts": [],
        "solution_count": count,
        "unique": count == 1,
        "solution": format_board(solutions[0]) if count == 1 else None,
    }
    if with_difficulty:
        # Difficulty only means something when there's exactly one answer
        # to reach -- a board with zero or many solutions isn't "hard",
        # it's just not a real puzzle.
        result["difficulty"] = estimate_difficulty(grid) if count == 1 else None
    return result


def _print_human(result: dict) -> None:
    if not result["valid"]:
        print("invalid board:")
        for conflict in result["conflicts"]:
            print(f"  - {conflict}")
        return

    if result["solution_count"] == 0:
        print("no solution exists for this board")
    elif result["unique"]:
        print("unique solution:")
        print(result["solution"])
        if result.get("difficulty"):
            print(f"difficulty: {result['difficulty']}")
    else:
        print("multiple solutions exist -- this board does not have a unique answer")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sudoku-unique",
        description="Check whether a Sudoku board has exactly one solution.",
    )
    parser.add_argument(
        "board",
        nargs="?",
        help=(
            "81-cell board (digits 1-9, '.' or '0' for empty), a path to a file "
            "containing one board or several (one 81-cell line each), or '-' to "
            "read from stdin. Not used with --generate"
        ),
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    parser.add_argument(
        "--difficulty",
        action="store_true",
        help=(
            "estimate difficulty from the solving techniques required "
            "(only meaningful for boards with a unique solution)"
        ),
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="generate a random puzzle with a unique solution instead of checking one",
    )
    parser.add_argument(
        "--clues",
        type=int,
        default=None,
        help=(
            "target number of filled cells when generating with --generate "
            "(fewer clues takes longer to dig and isn't guaranteed exactly)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="random seed for --generate, for reproducible output",
    )
    args = parser.parse_args(argv)

    if args.generate:
        if args.board is not None:
            parser.error("a board argument can't be combined with --generate")
        if args.clues is not None and not (0 <= args.clues <= BOARD_SIZE * BOARD_SIZE):
            parser.error("--clues must be between 0 and 81")
        grid = generate_puzzle(clues=args.clues, rng=random.Random(args.seed))
        board_text = format_board(grid)
        if args.json:
            print(json.dumps({"board": board_text.replace("\n", "")}))
        else:
            print(board_text)
        return 0

    if args.board is None:
        parser.error("board is required unless --generate is given")

    try:
        board_text = _read_board_text(args.board)
        boards = split_boards(board_text)
        results = [build_result(board, with_difficulty=args.difficulty) for board in boards]
    except InvalidBoard as exc:
        if args.json:
            print(json.dumps({"valid": False, "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if len(results) == 1:
        if args.json:
            print(json.dumps(results[0]))
        else:
            _print_human(results[0])
        return 0 if results[0]["valid"] else 1

    if args.json:
        print(json.dumps(results))
    else:
        for i, result in enumerate(results, start=1):
            print(f"board {i}:")
            _print_human(result)
            print()

    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
