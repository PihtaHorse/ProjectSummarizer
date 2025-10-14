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
    # directories first (sorted), then files
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


def aggregate_totals(file_paths: List[str]) -> Dict[str, int]:
    # size is not available here; caller should compute if needed
    return {"files": len(file_paths)}


