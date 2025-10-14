import argparse
import os
import logging
from dotenv import load_dotenv
from projectsummarizer.core.ignore import collect_file_paths
from projectsummarizer.core.tokens import get_all_content_counts
from projectsummarizer.core.tree import build_augmented_tree, print_augmented_tree


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


def _build_augmented_tree(rel_paths, metrics, models):
    root = {}
    for rel in rel_paths:
        parts = rel.split("/")
        node = root
        for idx, part in enumerate(parts):
            is_file = idx == len(parts) - 1
            if is_file:
                files = node.setdefault("__files__", [])
                files.append(part)
                # store per-file metrics
                file_key = ("__file_meta__", part)
                node[file_key] = metrics[rel]
            else:
                node = node.setdefault(part, {})
            # accumulate aggregates on every node along the path
            agg = node.setdefault("__agg__", {"size": 0, "tokens": {}})
        # After adding file, bubble up aggregates
        # Walk again to add this file's metrics to parents
        node = root
        acc_path = []
        for idx, part in enumerate(parts):
            acc_path.append(part)
            is_file = idx == len(parts) - 1
            if is_file:
                # add metrics to this directory's agg
                dir_node = node
            else:
                dir_node = node.setdefault(part, {})
            agg = dir_node.setdefault("__agg__", {"size": 0, "tokens": {}})
            agg["size"] += metrics[rel]["size"]
            if models:
                for m, v in metrics[rel]["tokens"].items():
                    agg["tokens"][m] = agg["tokens"].get(m, 0) + v
            if not is_file:
                node = dir_node
    # compute root aggregates
    root.setdefault("__agg__", {"size": 0, "tokens": {}})
    return root


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

    # metrics
    models = args.count_tokens or []
    metrics = _gather_file_metrics(args.directory, file_paths, models)

    # augmented tree with per-node aggregates
    tree = build_augmented_tree(file_paths, metrics, models)
    root_agg = tree.get("__agg__", {"size": 0, "tokens": {}})

    # print totals first
    print(f"Total files: {len(file_paths)}")
    print(f"Total size (bytes): {root_agg.get('size', 0)}")
    if models:
        for m in models:
            print(f"Total Token Count ({m}): {root_agg.get('tokens', {}).get(m, 0)}")
    print()  # empty line separator

    # print tree
    print(print_augmented_tree(tree, models))


if __name__ == "__main__":
    main()


