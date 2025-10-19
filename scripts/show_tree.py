import argparse
from projectsummarizer.engine import build_tree, render_ascii_tree


def main():
    parser = argparse.ArgumentParser(description="Show project tree with byte sizes and optional token counts.")
    parser.add_argument("--directory", required=True, help="Project root")
    parser.add_argument("--ignore_patterns", default="", help="Comma-separated extra patterns")
    parser.add_argument("--no_defaults", action="store_true", help="Do not apply default ignore patterns")
    parser.add_argument("--include_binary", action="store_true", help="Include binary files")
    parser.add_argument("--no_gitignore", action="store_true", help="Do not read .gitignore files")
    parser.add_argument(
        "--filter",
        type=str,
        choices=["included", "removed", "all"],
        default="included",
        help="Which files to show: 'included' (default, after ignore patterns), 'removed' (ignored files), or 'all' (no filtering)"
    )
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify one or more models to count tokens for (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')."
    )
    args = parser.parse_args()

    user_patterns = [pattern for pattern in args.ignore_patterns.split(",") if pattern] if args.ignore_patterns else []

    root = build_tree(
        args.directory,
        ignore_patterns=user_patterns,
        use_defaults=not args.no_defaults,
        include_binary=args.include_binary,
        read_ignore_files=not args.no_gitignore,
        token_models=args.count_tokens or [],
        filter_type=args.filter,
    )
    print(render_ascii_tree(root))


if __name__ == "__main__":
    main()

