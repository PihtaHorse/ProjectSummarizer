from typing import Dict, List, Any


def build_tree_structure(file_paths: List[str]) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    for path in file_paths:
        parts = path.split("/")
        node = root
        for idx, part in enumerate(parts):
            if idx == len(parts) - 1:
                node.setdefault("__files__", []).append(part)
            else:
                node = node.setdefault(part, {})
    return root


def _print_tree(node: Dict[str, Any], prefix: str = "") -> List[str]:
    lines: List[str] = []
    dirs = sorted([k for k in node.keys() if k != "__files__"])
    files = sorted(node.get("__files__", []))

    for d in dirs:
        lines.append(f"{prefix}{d}/")
        lines.extend(_print_tree(node[d], prefix + "  "))

    for f in files:
        lines.append(f"{prefix}{f}")
    return lines


def print_tree(tree: Dict[str, Any]) -> str:
    return "\n".join(_print_tree(tree))


def build_augmented_tree(
    rel_paths: List[str],
    metrics: Dict[str, Dict[str, Any]],
    models: List[str],
) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    for rel in rel_paths:
        parts = rel.split("/")
        # create nodes and record file entry + file meta
        node = root
        for idx, part in enumerate(parts):
            is_file = idx == len(parts) - 1
            if is_file:
                node.setdefault("__files__", []).append(part)
                node[("__file_meta__", part)] = metrics.get(rel, {"size": 0, "tokens": {}})
            else:
                node = node.setdefault(part, {})

        # bubble up aggregates along the path
        node = root
        for idx, part in enumerate(parts):
            is_file = idx == len(parts) - 1
            if is_file:
                dir_node = node
            else:
                dir_node = node.setdefault(part, {})
            agg = dir_node.setdefault("__agg__", {"size": 0, "tokens": {}})
            file_metrics = metrics.get(rel, {"size": 0, "tokens": {}})
            agg["size"] += int(file_metrics.get("size", 0))
            if models:
                for m, v in file_metrics.get("tokens", {}).items():
                    agg["tokens"][m] = agg["tokens"].get(m, 0) + int(v)
            if not is_file:
                node = dir_node

    root.setdefault("__agg__", {"size": 0, "tokens": {}})
    return root


def _format_meta(size: int, tokens: Dict[str, int], models: List[str]) -> str:
    parts: List[str] = [f"{size}B"]
    if models and tokens:
        parts.append(", ".join([f"{m}:{tokens.get(m, 0)}" for m in models]))
    return " (" + "; ".join(parts) + ")"


def print_augmented_tree(tree: Dict[str, Any], models: List[str]) -> str:
    lines: List[str] = []

    def list_dir_entries(node: Dict[str, Any]) -> List[Any]:
        dir_names = sorted(
            [
                k
                for k in node.keys()
                if k not in ("__files__", "__agg__") and not (isinstance(k, tuple) and k[0] == "__file_meta__")
            ]
        )
        file_names = sorted(node.get("__files__", []))
        return [("dir", name) for name in dir_names] + [("file", name) for name in file_names]

    def walk(node: Dict[str, Any], prefixes: List[str]) -> None:
        entries = list_dir_entries(node)
        last_index = len(entries) - 1
        for idx, (kind, name) in enumerate(entries):
            is_last = idx == last_index
            branch = "└── " if is_last else "├── "
            indent = "".join(prefixes) + branch

            if kind == "dir":
                child = node[name]
                agg = child.get("__agg__", {"size": 0, "tokens": {}})
                meta = _format_meta(int(agg.get("size", 0)), {k: int(v) for k, v in agg.get("tokens", {}).items()}, models)
                lines.append(f"{indent}{name}/" + meta)
                next_prefix = "    " if is_last else "│   "
                walk(child, prefixes + [next_prefix])
            else:
                file_meta = node.get(("__file_meta__", name), {"size": 0, "tokens": {}})
                meta = _format_meta(int(file_meta.get("size", 0)), {k: int(v) for k, v in file_meta.get("tokens", {}).items()}, models)
                lines.append(f"{indent}{name}" + meta)

    walk(tree, [])
    return "\n".join(lines)


