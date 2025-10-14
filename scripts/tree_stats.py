import argparse
import os
import logging
from dotenv import load_dotenv
from projectsummarizer.core.ignore import collect_file_paths
from projectsummarizer.core.tokens import get_all_content_counts
from projectsummarizer.core.tree import build_augmented_tree, print_augmented_tree
from projectsummarizer.constants import DEFAULT_IGNORE_PATTERNS, BINARY_IGNORE_PATTERNS


load_dotenv()
logging.basicConfig(level=logging.INFO)


def _safe_read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def _gather_file_metrics(directory: str, rel_paths, models):
    per_file = {}
    for rel in rel_paths:
        full = os.path.join(directory, rel)
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0
        tokens = {}
        if models:
            content = _safe_read_text(full)
            if content:
                counts = get_all_content_counts(content, models)
                for m in models:
                    tokens[m] = counts.get(m, 0)
        per_file[rel] = {"size": size, "tokens": tokens}
    return per_file


def _format_meta(size: int, tokens: dict, models) -> str:
    parts = [f"{size}B"]
    if models and tokens:
        tok_parts = [f"{m}:{tokens.get(m, 0)}" for m in models]
        parts.append(", ".join(tok_parts))
    return " (" + "; ".join(parts) + ")"


def _print_augmented(node, models, prefix=""):
    lines = []
    # directories first (sorted), then files
    dirs = sorted([k for k in node.keys() if k not in ("__files__", "__agg__") and not (isinstance(k, tuple) and k[0] == "__file_meta__")])
    files = sorted(node.get("__files__", []))

    for d in dirs:
        child = node[d]
        agg = child.get("__agg__", {"size": 0, "tokens": {}})
        meta = _format_meta(agg.get("size", 0), agg.get("tokens", {}), models)
        lines.append(f"{prefix}{d}/" + meta)
        lines.extend(_print_augmented(child, models, prefix + "  "))

    for f in files:
        file_meta = node.get(("__file_meta__", f), {"size": 0, "tokens": {}})
        meta = _format_meta(file_meta.get("size", 0), file_meta.get("tokens", {}), models)
        lines.append(f"{prefix}{f}" + meta)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Print folder tree with totals and optional token counts.")
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
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify models to count tokens for",
    )
    parser.add_argument(
        "--list_extensions",
        type=str,
        choices=["all", "effective", "removed"],
        help="Show tree for specific file sets: 'all' (all files), 'effective' (included files), 'removed' (ignored files)",
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
    
    # Determine which files to show based on list_extensions flag
    if args.list_extensions == "all":
        # Show all files (no ignore patterns)
        file_paths = collect_file_paths(args.directory, [], include_ignore_files=False)
        print("📁 Showing ALL files (no ignore patterns applied)")
    elif args.list_extensions == "removed":
        # Show only ignored files
        all_files = collect_file_paths(args.directory, [], include_ignore_files=False)
        effective_files = collect_file_paths(args.directory, global_patterns, include_ignore_files=True)
        file_paths = [f for f in all_files if f not in effective_files]
        print("🚫 Showing REMOVED files (ignored by patterns)")
    else:
        # Default: show effective files (included files)
        file_paths = collect_file_paths(args.directory, global_patterns, include_ignore_files=True)
        print("✅ Showing EFFECTIVE files (included after ignore patterns)")

    # metrics
    models = args.count_tokens or []
    metrics = _gather_file_metrics(args.directory, file_paths, models)

    # augmented tree with per-node aggregates
    tree = build_augmented_tree(file_paths, metrics, models)
    root_agg = tree.get("__agg__", {"size": 0, "tokens": {}})

    # Calculate stats from tree structure to ensure alignment
    def count_files_in_tree(node):
        """Recursively count files in tree structure"""
        count = 0
        files = node.get("__files__", [])
        count += len(files)
        
        # Count files in subdirectories
        for key, value in node.items():
            if key not in ("__files__", "__agg__") and not (isinstance(key, tuple) and key[0] == "__file_meta__"):
                count += count_files_in_tree(value)
        return count

    total_files_from_tree = count_files_in_tree(tree)
    total_size_from_tree = root_agg.get('size', 0)
    total_tokens_from_tree = root_agg.get('tokens', {})

    # print totals first (from tree structure)
    print(f"Total files: {total_files_from_tree}")
    print(f"Total size (bytes): {total_size_from_tree}")
    if models:
        for m in models:
            print(f"Total Token Count ({m}): {total_tokens_from_tree.get(m, 0)}")
    print()  # empty line separator

    # print tree
    print(print_augmented_tree(tree, models))


if __name__ == "__main__":
    main()


