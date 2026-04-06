#!/usr/bin/env python3
"""Project summarization script - generates structured project summaries."""

import argparse
import logging
import sys
from pathlib import Path

import pyperclip
from dotenv import load_dotenv

from projectsummarizer.call_logger import log_call
from projectsummarizer.engine import build_tree, render_ascii_tree
from projectsummarizer.contents.formatters import create_formatter
from projectsummarizer.cli import (
    add_file_selection_args,
    add_ignore_logic_args,
    add_token_counting_args,
    add_sorting_args,
    add_date_tracking_args,
    add_format_args,
)


load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize project files, optionally including their contents."
    )

    # Add common argument groups
    add_file_selection_args(parser, directory_required=True)
    add_ignore_logic_args(parser)
    add_token_counting_args(parser)
    add_sorting_args(parser)
    add_date_tracking_args(parser)
    add_format_args(parser)

    # Script-specific arguments
    parser.add_argument(
        "--output_file", type=str, default="summary.txt", required=False, help="Output file to write the contents"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy the generated summary to the clipboard instead of saving it to a file",
    )
    parser.add_argument(
        "--special_character",
        type=str,
        required=False,
        default="```",
        help="Special character to use as a delimiter for file content",
    )
    parser.add_argument(
        "--delimiter_replacement",
        type=str,
        required=False,
        default="'''",
        help="String to replace delimiter with in file contents to prevent breaking out of blocks",
    )
    parser.add_argument(
        "--only_structure",
        action="store_true",
        help="If set, only output the project structure without file contents"
    )

    args = parser.parse_args()

    # Validate sorting arguments
    if args.sort_by in ["created", "modified"]:
        # Date sorting requires --include-dates
        if not args.include_dates:
            parser.error(
                f"When sorting by '{args.sort_by}', --include-dates must be enabled"
            )
    elif args.sort_by not in ["name", "size"]:
        # Treat as token model - must be in count_tokens
        if not args.count_tokens or args.sort_by not in args.count_tokens:
            parser.error(
                f"When sorting by token model '{args.sort_by}', "
                f"it must be included in --count_tokens"
            )

    # Add user-specified patterns
    user_patterns = []
    if args.ignore:
        user_patterns.extend(args.ignore.split(","))

    # Create formatter - it owns the output file
    output_path = Path(args.output_file)

    formatter = create_formatter(
        args.format,
        str(output_path),
        delimiter=args.special_character,
        delimiter_replacement=args.delimiter_replacement,
    )

    # Build tree and stream content in ONE pass
    logging.info("Building file tree and streaming content...")

    with formatter:
        # Build tree - files read ONCE, content streamed via formatter callback
        root = build_tree(
            args.directory,
            ignore_patterns=user_patterns,
            use_defaults=not args.no_defaults,
            include_binary=args.include_binary,
            read_ignore_files=not args.no_gitignore,
            token_models=args.count_tokens or [],
            filter_type=args.filter,
            content_processor=formatter.write_content if not args.only_structure else None,
            level=args.level,
            include_dates=args.include_dates,
        )

        # Prepend tree structure at the beginning (without stats for cleaner output)
        tree_structure = render_ascii_tree(root, show_stats=False, sort_by=args.sort_by)
        formatter.write_tree(tree_structure)

    # Log statistics
    if not args.only_structure:
        logging.info(f"Total files processed: {formatter.file_count}")

    if args.clipboard:
        try:
            summary_text = output_path.read_text(encoding="utf-8")
            pyperclip.copy(summary_text)
        except FileNotFoundError:
            logging.error("Cannot copy summary: %s does not exist", output_path)
        except pyperclip.PyperclipException as exc:
            logging.error("Failed to copy summary to clipboard: %s", exc)
            logging.info(f"Output written to: {output_path}")
        else:
            output_path.unlink(missing_ok=True)
            logging.info("Summary copied to clipboard")
    else:
        logging.info(f"Output written to: {output_path}")

    # Log token counts if requested
    if args.count_tokens:
        # Use tree's built-in aggregation (root.tokens automatically sums all child tokens)
        for model, token_count in root.tokens.items():
            logging.info(f"Total Token Count ({model}): {token_count}")

    log_call(sys.argv, args.directory)


if __name__ == "__main__":
    main()
