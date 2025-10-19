#!/usr/bin/env python3
"""Project summarization script - generates structured project summaries."""

import argparse
import logging
from dotenv import load_dotenv

from projectsummarizer.engine import build_tree
from projectsummarizer.contents.formatters import StreamingTextFormatter


load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize project files, optionally including their contents."
    )
    parser.add_argument(
        "--directory", type=str, required=True, help="Directory path containing the files"
    )
    parser.add_argument(
        "--special_character",
        type=str,
        required=False,
        default="```",
        help="Special character to use as a delimiter for file content",
    )
    parser.add_argument(
        "--output_file", type=str, default="summary.txt", required=False, help="Output file to write the contents"
    )
    parser.add_argument(
        "--ignore_patterns",
        type=str,
        default="",
        help="Comma-separated list of additional patterns to ignore (added to defaults)",
    )
    parser.add_argument(
        "--include_binary",
        action="store_true",
        help="Include binary file types (images, videos, audio, archives, executables, etc.) - by default these are excluded",
    )
    parser.add_argument(
        "--no_defaults",
        action="store_true",
        help="Don't use default ignore patterns, only use patterns from --ignore_patterns",
    )
    parser.add_argument(
        "--only_structure",
        action="store_true",
        help="If set, only output the project structure without file contents"
    )
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify one or more models to count tokens for (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')."
    )
    parser.add_argument(
        "--filter",
        type=str,
        choices=["included", "removed", "all"],
        default="included",
        help="Which files to process: 'included' (default, after ignore patterns), 'removed' (ignored files), or 'all' (no filtering)"
    )

    args = parser.parse_args()

    # Add user-specified patterns
    user_patterns = []
    if args.ignore_patterns:
        user_patterns.extend(args.ignore_patterns.split(","))

    # Create formatter
    formatter = StreamingTextFormatter(delimiter=args.special_character)

    # Build tree and stream content in ONE pass
    logging.info("Building file tree and streaming content...")

    with open(args.output_file, "w+", encoding="utf-8") as outfile:
        content_writer = formatter.create_content_writer(outfile) if not args.only_structure else None

        root = build_tree(
            args.directory,
            ignore_patterns=user_patterns,
            use_defaults=not args.no_defaults,
            include_binary=args.include_binary,
            read_ignore_files=True,
            token_models=args.count_tokens or [],
            filter_type=args.filter,
            content_processor=content_writer,
        )

        # Now write structure at the beginning by rewriting the file
        # Read what was written (content section)
        outfile.seek(0)
        content_data = outfile.read()

        # Rewrite file: structure first, then content
        outfile.seek(0)
        outfile.truncate()
        formatter.write_structure(root, outfile)
        outfile.write(content_data)

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
