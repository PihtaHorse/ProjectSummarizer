import argparse
import logging
import os
from dotenv import load_dotenv
from typing import List
from prettytable import PrettyTable

from projectsummarizer.core.ignore import collect_file_paths
from projectsummarizer.core.analysis import compute_extension_stats, compute_token_stats_by_extension
from projectsummarizer.constants import DEFAULT_IGNORE_PATTERNS, BINARY_IGNORE_PATTERNS


load_dotenv()
logging.basicConfig(level=logging.INFO)


def format_size(size: int) -> str:
    # simple human readable sizes
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size}{unit}"
        size //= 1024
    return f"{size}TB"


def main():
    parser = argparse.ArgumentParser(description="List extensions (all/effective/removed) and suggest ignore patterns.")
    parser.add_argument("--directory", type=str, required=True, help="Directory path containing the files")
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
        "--list_extensions",
        type=str,
        choices=["all", "effective", "removed"],
        default="effective",
        help="Which set of extensions to list",
    )
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify models to count tokens for",
    )
    args = parser.parse_args()

    # Build ignore patterns based on flags
    global_patterns = []
    
    if not args.no_defaults:
        # Include default patterns (security, cache, etc.)
        global_patterns.extend(DEFAULT_IGNORE_PATTERNS)
        # Include binary patterns by default
        global_patterns.extend(BINARY_IGNORE_PATTERNS)
    elif args.include_binary:
        # If no-defaults but include-binary, only add binary patterns
        global_patterns.extend(BINARY_IGNORE_PATTERNS)
    
    # Add user-specified patterns
    if args.ignore_patterns:
        global_patterns.extend(args.ignore_patterns.split(","))

    # all files (no ignore files)
    all_files = collect_file_paths(args.directory, [], include_ignore_files=False)
    all_stats = compute_extension_stats(args.directory, all_files)

    # effective files (apply global + ignore files)
    effective_files = collect_file_paths(args.directory, global_patterns, include_ignore_files=True)
    effective_stats = compute_extension_stats(args.directory, effective_files)

    # removed = all - effective
    removed_stats = {ext: all_stats[ext] for ext in all_stats.keys() - effective_stats.keys()}

    selection = {
        "all": all_stats,
        "effective": effective_stats,
        "removed": removed_stats,
    }[args.list_extensions]

    # token stats (optional)
    tokens_by_ext = {}
    if args.count_tokens:
        files_for_tokens = (
            all_files if args.list_extensions == "all" else effective_files if args.list_extensions == "effective" else [
                f for f in all_files if f not in set(effective_files)
            ]
        )
        tokens_by_ext = compute_token_stats_by_extension(args.directory, files_for_tokens, args.count_tokens)

    # print table
    has_tokens = bool(args.count_tokens)
    
    # Create table
    table = PrettyTable()
    table.field_names = ["extension", "count", "size"] + (args.count_tokens if has_tokens else [])
    table.align["extension"] = "l"
    table.align["count"] = "r"
    table.align["size"] = "r"
    if has_tokens:
        for m in args.count_tokens:
            table.align[m] = "r"
    
    # Add rows (sorted by size descending)
    for ext in sorted(selection.keys(), key=lambda x: selection[x]["size"], reverse=True):
        row = [
            ext or "(noext)",
            selection[ext]["count"],
            format_size(selection[ext]["size"]),
        ]
        if has_tokens:
            for m in args.count_tokens:
                row.append(tokens_by_ext.get(ext, {}).get(m, 0))
        table.add_row(row)
    
    print(table)

    # suggest patterns
    patterns = []
    for ext in sorted(selection.keys()):
        if ext == "":
            continue
        patterns.append(f"*.{ext}")
    if patterns:
        print()
        print(",".join(patterns))


if __name__ == "__main__":
    main()


