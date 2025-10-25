"""Common argument definitions for ProjectSummarizer CLI scripts.

This module provides reusable argument groups that are shared across
multiple scripts (show_tree.py, summarize.py, simple_stats.py).

Script-specific arguments should remain in their respective scripts.
"""

import argparse
from typing import Optional


def add_file_selection_args(
    parser: argparse.ArgumentParser,
    directory_required: bool = True,
    directory_default: Optional[str] = None
) -> None:
    """Add file selection arguments to parser.

    Args:
        parser: ArgumentParser to add arguments to
        directory_required: Whether --directory is required (default: True)
        directory_default: Default value for --directory if not required
    """
    parser.add_argument(
        "--directory",
        type=str,
        required=directory_required,
        default=directory_default,
        help="Project root directory to analyze"
    )

    parser.add_argument(
        "--filter",
        type=str,
        choices=["included", "removed", "all"],
        default="included",
        help="Which files to show: 'included' (default, after ignore patterns), "
             "'removed' (ignored files), or 'all' (no filtering)"
    )


def add_ignore_logic_args(parser: argparse.ArgumentParser) -> None:
    """Add ignore pattern and filtering arguments to parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        "-I", "--ignore",
        type=str,
        default="",
        dest="ignore",
        help="Comma-separated patterns to ignore (e.g., '*.log,temp*'). "
             "Supports gitignore-style negation with '!' prefix to create exceptions "
             "(e.g., '*.log,!important.log' ignores all .log files except important.log). "
             "Added to defaults unless --no_defaults is used."
    )

    parser.add_argument(
        "--no_defaults",
        action="store_true",
        help="Don't use default ignore patterns, only use patterns from -I/--ignore"
    )

    parser.add_argument(
        "--no_gitignore",
        action="store_true",
        help="Do not read .gitignore files"
    )

    parser.add_argument(
        "--include_binary",
        action="store_true",
        help="Include binary file types (images, videos, audio, archives, executables, etc.) "
             "- by default these are excluded"
    )


def add_token_counting_args(parser: argparse.ArgumentParser) -> None:
    """Add token counting arguments to parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        help="Specify one or more models to count tokens for. "
             "Supports OpenAI (e.g. 'gpt-4o'), Anthropic (e.g. 'claude-3-5-sonnet-20241022'), "
             "and Google (e.g. 'gemini-1.5-pro-002') models."
    )
