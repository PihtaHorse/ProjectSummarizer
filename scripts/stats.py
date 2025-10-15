import argparse
import logging
import os
import fnmatch
from dotenv import load_dotenv
from prettytable import PrettyTable

from projectsummarizer.core.ignore import collect_file_paths, parse_ignore_files
from projectsummarizer.core.analysis import compute_extension_stats, compute_token_stats_by_extension
from projectsummarizer.core.tokens import get_all_content_counts
from projectsummarizer.core.tree import build_augmented_tree, print_augmented_tree
from projectsummarizer.constants import DEFAULT_IGNORE_PATTERNS, BINARY_IGNORE_PATTERNS
from projectsummarizer.core.left_patterns import compute_minimal_left_patterns


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


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size}{unit}"
        size //= 1024
    return f"{size}TB"


def _build_global_patterns(use_defaults: bool, include_binary_only_when_no_defaults: bool, user_patterns: str):
    patterns = []
    if use_defaults:
        patterns.extend(DEFAULT_IGNORE_PATTERNS)
        patterns.extend(BINARY_IGNORE_PATTERNS)
    elif include_binary_only_when_no_defaults:
        patterns.extend(BINARY_IGNORE_PATTERNS)
    if user_patterns:
        patterns.extend(user_patterns.split(","))
    return patterns


def _resolve_file_sets(directory: str, global_patterns: list, selection: str):
    if selection == "all":
        all_files = collect_file_paths(directory, [], include_ignore_files=False)
        effective_files = collect_file_paths(directory, global_patterns, include_ignore_files=True)
        removed_files = [f for f in all_files if f not in set(effective_files)]
        return all_files, effective_files, removed_files
    # default resolve both lists for derived computations
    all_files = collect_file_paths(directory, [], include_ignore_files=False)
    effective_files = collect_file_paths(directory, global_patterns, include_ignore_files=True)
    removed_files = [f for f in all_files if f not in set(effective_files)]
    return all_files, effective_files, removed_files


def _gather_ignore_file_patterns(directory: str):
    patterns = set()
    # include top-level ignore files
    for p in parse_ignore_files(directory):
        patterns.add(p)
    # include ignore files from subdirectories
    for root, _, _ in os.walk(directory, topdown=True):
        if root == directory:
            continue
        for p in parse_ignore_files(root):
            patterns.add(p)
    return sorted(patterns)


def _run_tree_mode(directory: str, file_paths, models):
    metrics = _gather_file_metrics(directory, file_paths, models)
    tree = build_augmented_tree(file_paths, metrics, models)
    root_agg = tree.get("__agg__", {"size": 0, "tokens": {}})

    def _count_files(node):
        count = 0
        files = node.get("__files__", [])
        count += len(files)
        for key, value in node.items():
            if key not in ("__files__", "__agg__") and not (isinstance(key, tuple) and key[0] == "__file_meta__"):
                count += _count_files(value)
        return count

    total_files = _count_files(tree)
    total_size = root_agg.get("size", 0)
    total_tokens = root_agg.get("tokens", {})

    print(f"Total files: {total_files}")
    print(f"Total size (bytes): {total_size}")
    if models:
        for m in models:
            print(f"Total Token Count ({m}): {total_tokens.get(m, 0)}")
    print()
    print(print_augmented_tree(tree, models))


def _run_table_mode(directory: str, selection_stats: dict, tokens_by_ext: dict, models):
    has_tokens = bool(models)
    table = PrettyTable()
    table.field_names = ["extension", "count", "size"] + (models if has_tokens else [])
    table.align["extension"] = "l"
    table.align["count"] = "r"
    table.align["size"] = "r"
    if has_tokens:
        for m in models:
            table.align[m] = "r"
    for ext in sorted(selection_stats.keys(), key=lambda x: selection_stats[x]["size"], reverse=True):
        row = [ext or "(noext)", selection_stats[ext]["count"], _format_size(selection_stats[ext]["size"])]
        if has_tokens:
            for m in models:
                row.append(tokens_by_ext.get(ext, {}).get(m, 0))
        table.add_row(row)
    print(table)


def main():
    parser = argparse.ArgumentParser(description="Project statistics: tree and table views")
    parser.add_argument("--directory", type=str, required=True, help="Directory path containing the files")
    parser.add_argument("--ignore_patterns", type=str, default="", help="Comma-separated additional patterns to ignore")
    parser.add_argument("--include-binary", action="store_true", help="Include binary patterns when --no-defaults is set")
    parser.add_argument("--no-defaults", action="store_true", help="Only use patterns from --ignore_patterns (and optional binary)")
    parser.add_argument("--list_extensions", type=str, choices=["all", "effective", "removed"], default="effective", help="Which file set to use for outputs")
    parser.add_argument("--count_tokens", type=str, nargs="*", choices=["gpt-4o", "claude-3-5-sonnet-20241022"], help="Models to count tokens for")
    parser.add_argument("--mode", type=str, choices=["both", "tree", "table"], default="both", help="Which output to show")
    parser.add_argument("--print-left", action="store_true", help="Print minimal umbrella patterns for included files")
    args = parser.parse_args()

    use_defaults = not args.no_defaults
    global_patterns = _build_global_patterns(use_defaults, args.include_binary, args.ignore_patterns)

    all_files, effective_files, removed_files = _resolve_file_sets(args.directory, global_patterns, args.list_extensions)

    if args.list_extensions == "all":
        selection_files = all_files
        print("Showing ALL files (no ignore patterns applied)")
    elif args.list_extensions == "removed":
        selection_files = removed_files
        print("Showing REMOVED files (ignored by patterns)")
    else:
        selection_files = effective_files
        print("Showing EFFECTIVE files (included after ignore patterns)")

    models = args.count_tokens or []

    if args.mode in ("both", "tree"):
        _run_tree_mode(args.directory, selection_files, models)

    if args.mode in ("both", "table"):
        all_stats = compute_extension_stats(args.directory, all_files)
        effective_stats = compute_extension_stats(args.directory, effective_files)
        removed_stats = {ext: all_stats[ext] for ext in all_stats.keys() - effective_stats.keys()}
        if args.list_extensions == "all":
            selection_stats = all_stats
        elif args.list_extensions == "removed":
            selection_stats = removed_stats
        else:
            selection_stats = effective_stats

        tokens_by_ext = {}
        if models:
            files_for_tokens = selection_files
            tokens_by_ext = compute_token_stats_by_extension(args.directory, files_for_tokens, models)

        _run_table_mode(args.directory, selection_stats, tokens_by_ext, models)

        # After table, print effective patterns only
        ignore_file_patterns = _gather_ignore_file_patterns(args.directory)
        all_effective_patterns = list(global_patterns) + ignore_file_patterns

        # Filter effective patterns to only those that actually match removed files
        removed_set = set(removed_files)
        def pattern_matches_any_removed(pat: str) -> bool:
            for rel in removed_set:
                if fnmatch.fnmatchcase(rel, pat):
                    return True
            return False

        # Keep original patterns as-is (no folder normalization), but only those that matched
        effective_patterns = [p for p in all_effective_patterns if pattern_matches_any_removed(p)]

        if effective_patterns:
            print()
            print("effective patterns:")
            print(",".join(effective_patterns))

        if args.print_left:
            # Compute minimal umbrella patterns over included files (selection_files)
            left_patterns = compute_minimal_left_patterns(selection_files)
            if left_patterns:
                print()
                print("left patterns:")
                print("\n".join(left_patterns))


if __name__ == "__main__":
    main()


