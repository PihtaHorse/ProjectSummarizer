import os
from typing import Dict, List, Tuple


def _get_extension(path: str) -> str:
    base = os.path.basename(path)
    # handle files like ".gitignore" (treat as extension "gitignore")
    if base.startswith(".") and base.count(".") == 1:
        return base[1:].lower()
    ext = os.path.splitext(base)[1].lower()
    return ext[1:] if ext.startswith(".") else ext


def compute_extension_stats(directory: str, file_paths: List[str]) -> Dict[str, Dict[str, int]]:
    stats: Dict[str, Dict[str, int]] = {}
    for rel_path in file_paths:
        full_path = os.path.join(directory, rel_path)
        try:
            size = os.path.getsize(full_path)
        except OSError:
            continue
        ext = _get_extension(rel_path) or ""
        bucket = stats.setdefault(ext, {"count": 0, "size": 0})
        bucket["count"] += 1
        bucket["size"] += size
    return stats


def classify_extensions(
    all_stats: Dict[str, Dict[str, int]],
    effective_stats: Dict[str, Dict[str, int]],
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
    # effective: present in effective_stats
    effective = {ext: effective_stats[ext] for ext in effective_stats}
    # removed: present in all_stats but not in effective_stats
    removed = {ext: all_stats[ext] for ext in all_stats.keys() - effective_stats.keys()}
    return effective, removed


def compute_token_stats_by_extension(
    directory: str,
    file_paths: List[str],
    models: List[str],
) -> Dict[str, Dict[str, int]]:
    from .tokens import get_all_content_counts

    token_by_ext: Dict[str, Dict[str, int]] = {}
    for rel_path in file_paths:
        full_path = os.path.join(directory, rel_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            # skip binaries/unreadable
            continue
        counts = get_all_content_counts(content, models)
        ext = _get_extension(rel_path) or ""
        bucket = token_by_ext.setdefault(ext, {m: 0 for m in models})
        for m in models:
            bucket[m] = bucket.get(m, 0) + counts.get(m, 0)
    return token_by_ext


