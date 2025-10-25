import argparse
from projectsummarizer.engine import build_tree, render_ascii_tree
from projectsummarizer.cli import (
    add_file_selection_args,
    add_ignore_logic_args,
    add_token_counting_args,
    add_sorting_args,
    add_date_tracking_args,
)
from dotenv import load_dotenv
import logging


load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')


def main():
    parser = argparse.ArgumentParser(description="Show project tree with byte sizes and optional token counts.")

    # Add common argument groups
    add_file_selection_args(parser, directory_required=True)
    add_ignore_logic_args(parser)
    add_token_counting_args(parser)
    add_sorting_args(parser)
    add_date_tracking_args(parser)

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

    user_patterns = [pattern for pattern in args.ignore.split(",") if pattern] if args.ignore else []

    root = build_tree(
        args.directory,
        ignore_patterns=user_patterns,
        use_defaults=not args.no_defaults,
        include_binary=args.include_binary,
        read_ignore_files=not args.no_gitignore,
        token_models=args.count_tokens or [],
        filter_type=args.filter,
        level=args.level,
        include_dates=args.include_dates,
    )
    print(render_ascii_tree(root, show_stats=True, sort_by=args.sort_by))


if __name__ == "__main__":
    main()

