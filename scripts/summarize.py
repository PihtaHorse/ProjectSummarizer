#!/usr/bin/env python3
"""Project summarization script - generates structured project summaries."""

import argparse
import logging
from dotenv import load_dotenv

from projectsummarizer.engine import build_summary
from projectsummarizer.contents.formatters import TextFormatter


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
        "--include-binary",
        action="store_true",
        help="Include binary file types (images, videos, audio, archives, executables, etc.) - by default these are excluded",
    )
    parser.add_argument(
        "--no-defaults",
        action="store_true",
        help="Don't use default ignore patterns, only use patterns from --ignore_patterns",
    )
    parser.add_argument(
        "--only_structure",
        action="store_true",
        help="If set, only output the project structure without file contents"
    )
    parser.add_argument(
        "--max_file_size",
        type=int,
        default=5 * 1024 * 1024,
        help="Maximum file size (in bytes) to include in the summary. Default is 5 MB."
    )
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify one or more models to count tokens for (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')."
    )
    
    args = parser.parse_args()

    # Build ignore patterns based on flags
    global_patterns = []
    
    if not args.no_defaults:
        # Include default patterns (security, cache, etc.)
        # Note: These are now handled by IgnorePatternsHandler internally
        pass
    elif args.include_binary:
        # If no-defaults but include-binary, only add binary patterns
        # Note: This is handled by IgnorePatternsHandler internally
        pass
    
    # Add user-specified patterns
    user_patterns = []
    if args.ignore_patterns:
        user_patterns.extend(args.ignore_patterns.split(","))

    # Build summary
    root, content_map = build_summary(
        args.directory,
        ignore_patterns=user_patterns,
        use_defaults=not args.no_defaults,
        include_binary=args.include_binary,
        read_ignore_files=True,
        token_models=args.count_tokens or [],
        max_file_size=args.max_file_size,
    )

    # Generate formatted output
    formatter = TextFormatter(delimiter=args.special_character)
    output = formatter.format_summary(
        root,
        content_map,
        include_structure=True,
        include_contents=not args.only_structure,
    )

    # Write to output file
    with open(args.output_file, "w", encoding='utf-8') as outfile:
        outfile.write(output)

    # Log statistics
    total_files = len(content_map)
    total_character_count = len(output)
    
    logging.info(f"Total files processed: {total_files}")
    logging.info(f"Total Character Count: {total_character_count}")
    
    # Log token counts if requested
    if args.count_tokens:
        # Calculate total tokens from the tree
        def collect_tokens(node):
            total_tokens = {}
            if not node.is_dir and node.tokens:
                for model, count in node.tokens.items():
                    if model != "characters":
                        total_tokens[model] = total_tokens.get(model, 0) + count
            
            for child in node.children:
                child_tokens = collect_tokens(child)
                for model, count in child_tokens.items():
                    total_tokens[model] = total_tokens.get(model, 0) + count
            
            return total_tokens
        
        total_tokens = collect_tokens(root)
        for model, token_count in total_tokens.items():
            logging.info(f"Total Token Count ({model}): {token_count}")


if __name__ == "__main__":
    main()
