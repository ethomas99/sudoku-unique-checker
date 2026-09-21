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
    "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8...7"
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

## Multiple boards

A file (or stdin) with several boards, one 81-character line each, is
checked as a batch instead of a single puzzle:

```
$ cat boards.txt
53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8...7
1...........................................................................
$ python -m sudoku_unique.cli boards.txt
board 1:
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

board 2:
multiple solutions exist -- this board does not have a unique answer
```

With `--json`, the output is a JSON array of per-board result objects in
the same order as the input. A single board, whether given as one line or
wrapped across nine, still produces a single result object rather than a
one-element array.

## Difficulty estimate

Add `--difficulty` to estimate how hard a board is to solve by hand. The
estimate is based on which solving techniques are needed, not on how many
clues are given:

- `easy` -- naked-single elimination (a cell with only one legal digit
  left) finishes the board on its own.
- `medium` -- hidden-single elimination (a digit with only one legal cell
  left in some row, column, or box) is needed somewhere along the way.
- `hard` -- neither technique finishes the board; the rest can only be
  pinned down by guessing and backtracking.

Difficulty is only meaningful for a board with exactly one solution. For
boards that are invalid or don't have a unique solution, `difficulty` is
`null`/`None` rather than a guess.

```
$ python -m sudoku_unique.cli --difficulty \
    ".34678912672195348198342567859761423426853791713924856961537284287419635345286179"
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
difficulty: easy
```

Here a single cell is blank, and its row, column, and box between them
already contain the other eight digits, so naked-single elimination alone
finishes the board.

## Generating puzzles

`--generate` produces a random puzzle with a unique solution instead of
checking one you already have. It fills a random complete grid, then
removes cells one at a time, keeping each removal only if the board still
has exactly one solution without it. The output is a nine-line grid, the
same shape `--json` reports a solution in, but with `.` for the cells
left blank:

```
$ python -m sudoku_unique.cli --generate --seed 1
```

By default it digs until no more cells can be removed (a "minimal"
puzzle). `--clues N` stops digging once `N` filled cells remain instead --
it's a floor, not an exact count, since digging still stops early if the
puzzle goes minimal first. `--seed N` makes the output reproducible. A
board argument can't be combined with `--generate`; `--json` works the
same as it does for checking a board, wrapping the generated board string
in `{"board": "..."}`.

## JSON output

Add `--json` to get the same result as a single JSON object on stdout,
for scripting or feeding into another tool:

```
$ python -m sudoku_unique.cli --json "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8...7"
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
