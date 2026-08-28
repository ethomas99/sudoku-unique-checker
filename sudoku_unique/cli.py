"""Command-line entry point: does this Sudoku board have exactly one solution?"""

from __future__ import annotations

import argparse
import json
import sys

from .solver import InvalidBoard, count_solutions, find_conflicts, format_board, parse_board


def _read_board_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    try:
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Not a path -- treat the argument itself as the board text.
        return source


def build_result(board_text: str) -> dict:
    grid = parse_board(board_text)
    conflicts = find_conflicts(grid)
    if conflicts:
        return {
            "valid": False,
            "conflicts": conflicts,
            "solution_count": 0,
            "unique": False,
            "solution": None,
        }

    solutions = count_solutions(grid, limit=2)
    count = len(solutions)
    return {
        "valid": True,
        "conflicts": [],
        "solution_count": count,
        "unique": count == 1,
        "solution": format_board(solutions[0]) if count == 1 else None,
    }


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
    else:
        print("multiple solutions exist -- this board does not have a unique answer")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sudoku-unique",
        description="Check whether a Sudoku board has exactly one solution.",
    )
    parser.add_argument(
        "board",
        help=(
            "81-cell board (digits 1-9, '.' or '0' for empty), a path to a file "
            "containing one, or '-' to read from stdin"
        ),
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    args = parser.parse_args(argv)

    try:
        board_text = _read_board_text(args.board)
        result = build_result(board_text)
    except InvalidBoard as exc:
        if args.json:
            print(json.dumps({"valid": False, "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result))
    else:
        _print_human(result)

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
