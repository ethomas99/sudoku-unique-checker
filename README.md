# sudoku-unique

A Sudoku puzzle is only a real puzzle if it has exactly one solution. If a
board has two or more valid completions, whoever's solving it can't ever be
sure they got "the" answer. This tool answers that one question: given a
board, does it have exactly one solution, none, or more than one?

It's meant for people hand-building or generating puzzles who need to check
their work before publishing it, not for solving puzzles interactively.

## Usage

Pass the board as an 81-character string (digits `1`-`9`, `.` or `0` for
empty cells), a path to a file containing one, or `-` to read from stdin.

```
$ python -m sudoku_unique.cli \
    "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8.."
unique solution:
534678912
672195348
198342567
859761423
426853791
713924856
961537284
287419635
345286179
```

A board with two or more solutions:

```
$ python -m sudoku_unique.cli "1..........................................................................."
multiple solutions exist -- this board does not have a unique answer
```

A board that breaks the rules outright (duplicate in a row, column, or box)
gets flagged instead of silently reported as unsolvable:

```
$ python -m sudoku_unique.cli "11......................................................................."
invalid board:
  - row 1 has duplicate 1 at columns 1 and 2
```

## JSON output

Add `--json` to get the same result as a single JSON object on stdout,
for scripting or feeding into another tool:

```
$ python -m sudoku_unique.cli --json "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8.."
{"valid": true, "conflicts": [], "solution_count": 1, "unique": true, "solution": "534678912\n672195348\n198342567\n859761423\n426853791\n713924856\n961537284\n287419635\n345286179"}
```

Fields:

- `valid` -- `false` if the board itself breaks Sudoku's rules (a repeated
  digit in some row, column, or box), regardless of solvability.
- `conflicts` -- list of human-readable descriptions of rule violations,
  empty when `valid` is `true`.
- `solution_count` -- number of solutions found, capped at 2 (a board with
  many solutions still reports `2`, since anything past that doesn't change
  the uniqueness answer).
- `unique` -- `true` only when `solution_count == 1`.
- `solution` -- the completed board as a string with `\n` between rows, or
  `null` when there isn't exactly one solution.

## Why cap the solution count at 2?

An empty 9x9 board has over 6.6 billion solutions. Counting them all would
be slow and pointless -- the only thing that matters for "is this a valid
puzzle" is whether the count is 0, 1, or "more than 1". The solver stops as
soon as it finds a second solution.

## Requirements

Python 3.9 or newer. No third-party dependencies.

## Running tests

The test suite uses `pytest` (not needed to run the tool itself, only to
develop it):

```
$ pip install pytest
$ pytest
```

## Status

Early. The solver and CLI work for well-formed boards; error messages and
edge cases (boards that aren't 9x9, alternate input formats) are still
rough.
