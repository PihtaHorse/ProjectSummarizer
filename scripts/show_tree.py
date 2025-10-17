import argparse
from projectsummarizer.engine import build_tree_from_directory, render_ascii_tree


def main():
    ap = argparse.ArgumentParser(description="Show project tree with byte sizes and optional token counts.")
    ap.add_argument("--directory", required=True, help="Project root")
    ap.add_argument("--ignore_patterns", default="", help="Comma-separated extra patterns")
    ap.add_argument("--no-defaults", action="store_true", help="Do not apply DEFAULT_IGNORE_PATTERNS")
    ap.add_argument("--include-binary", action="store_true", help="Include binary patterns if --no-defaults")
    ap.add_argument("--no-gitignore", action="store_true", help="Do not read .gitignore files")
    ap.add_argument(
        "--filter",
        type=str,
        choices=["included", "removed", "all"],
        default="included",
        help="Which files to show: 'included' (default, after ignore patterns), 'removed' (ignored files), or 'all' (no filtering)"
    )
    ap.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify one or more models to count tokens for (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')."
    )
    args = ap.parse_args()

    user = [p for p in args.ignore_patterns.split(",") if p] if args.ignore_patterns else []

    root = build_tree_from_directory(
        args.directory,
        ignore_patterns=user,
        use_defaults=not args.no_defaults,
        include_binary=args.include_binary,
        read_ignore_files=not args.no_gitignore,
        token_models=args.count_tokens or [],
        filter_type=args.filter,
    )
    print(render_ascii_tree(root))


if __name__ == "__main__":
    main()

