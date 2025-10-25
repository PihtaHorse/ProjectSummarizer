#!/usr/bin/env python3
"""Project summarization script - generates structured project summaries."""

import argparse
import logging
from dotenv import load_dotenv

from projectsummarizer.engine import build_tree, render_ascii_tree
from projectsummarizer.contents.formatters import StreamingTextFormatter
from projectsummarizer.cli import (
    add_file_selection_args,
    add_ignore_logic_args,
    add_token_counting_args,
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

    # Script-specific arguments
    parser.add_argument(
        "--output_file", type=str, default="summary.txt", required=False, help="Output file to write the contents"
    )
    parser.add_argument(
        "--special_character",
        type=str,
        required=False,
        default="```",
        help="Special character to use as a delimiter for file content",
    )
    parser.add_argument(
        "--only_structure",
        action="store_true",
        help="If set, only output the project structure without file contents"
    )

    args = parser.parse_args()

    # Add user-specified patterns
    user_patterns = []
    if args.ignore:
        user_patterns.extend(args.ignore.split(","))

    # Create formatter - it owns the output file
    formatter = StreamingTextFormatter(
        output_path=args.output_file,
        delimiter=args.special_character
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
            read_ignore_files=True,
            token_models=args.count_tokens or [],
            filter_type=args.filter,
            content_processor=formatter.write_content if not args.only_structure else None,
        )

        # Prepend tree structure at the beginning (without stats for cleaner output)
        tree_structure = render_ascii_tree(root, show_stats=False)
        formatter.prepend(f"Project Structure:\n{tree_structure}\n")

    # Log statistics
    if not args.only_structure:
        logging.info(f"Total files processed: {formatter.file_count}")
    logging.info(f"Output written to: {args.output_file}")

    # Log token counts if requested
    if args.count_tokens:
        # Use tree's built-in aggregation (root.tokens automatically sums all child tokens)
        for model, token_count in root.tokens.items():
            logging.info(f"Total Token Count ({model}): {token_count}")


if __name__ == "__main__":
    main()
