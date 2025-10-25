import argparse
from projectsummarizer.engine import build_tree, render_ascii_tree
from projectsummarizer.cli import (
    add_file_selection_args,
    add_ignore_logic_args,
    add_token_counting_args,
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

    args = parser.parse_args()

    user_patterns = [pattern for pattern in args.ignore.split(",") if pattern] if args.ignore else []

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

