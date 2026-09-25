"""Checks that the packaging metadata in pyproject.toml is actually wired up.

There's no build/install step in this test run, so these can't catch every
way `pip install .` might go wrong, but they catch the two things that
would otherwise slip through unnoticed: a typo in the console script's
dotted path, and the version string drifting between pyproject.toml and
the package itself.
"""

import importlib
import pathlib
import re

import sudoku_unique
from sudoku_unique.cli import main

PYPROJECT_TEXT = (
    pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
).read_text(encoding="utf-8")


def test_console_script_entry_point_resolves_to_cli_main():
    match = re.search(r'sudoku-unique\s*=\s*"([^"]+)"', PYPROJECT_TEXT)
    assert match, "sudoku-unique entry point missing from pyproject.toml"

    module_path, attr = match.group(1).split(":")
    entry_point = getattr(importlib.import_module(module_path), attr)

    assert entry_point is main


def test_package_version_matches_pyproject():
    match = re.search(r'^version\s*=\s*"([^"]+)"', PYPROJECT_TEXT, re.MULTILINE)
    assert match, "version missing from pyproject.toml"

    assert sudoku_unique.__version__ == match.group(1)
