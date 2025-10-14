import argparse
import os
import logging
from dotenv import load_dotenv
from ps_core.ignore import collect_file_paths, parse_ignore_files
from ps_core.tree import build_tree_structure, print_tree
from ps_core.tokens import get_all_content_counts


load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Print folder tree with totals and optional token counts.")
    parser.add_argument("--directory", type=str, required=True, help="Directory path containing the files")
    parser.add_argument(
        "--ignore_patterns",
        type=str,
        default=".git,*.gitignore,*.dockerignore,*.png,*.jpg",
        help="Comma-separated list of patterns to ignore",
    )
    parser.add_argument(
        "--count_tokens",
        type=str,
        nargs="*",
        choices=["gpt-4o", "claude-3-5-sonnet-20241022"],
        help="Specify models to count tokens for",
    )
    args = parser.parse_args()

    global_patterns = args.ignore_patterns.split(",") if args.ignore_patterns else []
    file_paths = collect_file_paths(args.directory, global_patterns, include_ignore_files=True)

    # tree
    tree = build_tree_structure(file_paths)
    print(print_tree(tree))

    # totals
    total_files = len(file_paths)
    total_size = 0
    for rel in file_paths:
        try:
            total_size += os.path.getsize(os.path.join(args.directory, rel))
        except OSError:
            continue
    logging.info(f"Total files: {total_files}")
    logging.info(f"Total size (bytes): {total_size}")

    # tokens
    if args.count_tokens:
        content_chunks = []
        for rel in file_paths:
            full = os.path.join(args.directory, rel)
            try:
                with open(full, "r", encoding="utf-8") as f:
                    content_chunks.append(f.read())
            except (OSError, UnicodeDecodeError):
                continue
        content = "\n".join(content_chunks)
        counts = get_all_content_counts(content, args.count_tokens)
        for m in args.count_tokens:
            if m in counts:
                logging.info(f"Total Token Count ({m}): {counts[m]}")


if __name__ == "__main__":
    main()


