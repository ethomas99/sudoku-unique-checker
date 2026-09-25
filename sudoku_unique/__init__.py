"""sudoku_unique: answer one question -- does this board have exactly one solution?"""

from .solver import InvalidBoard, count_solutions, find_conflicts, parse_board

__version__ = "0.1.0"

__all__ = [
    "InvalidBoard",
    "count_solutions",
    "find_conflicts",
    "parse_board",
    "__version__",
]
