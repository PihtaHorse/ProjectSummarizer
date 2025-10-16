import os
from typing import Dict, List, Set, Tuple


def _split_path(rel: str) -> List[str]:
    return rel.split("/") if rel else []


def _ext_of(rel: str) -> str:
    base = os.path.basename(rel)
    if base.startswith(".") and base.count(".") == 1:
        return base[1:].lower()
    ext = os.path.splitext(base)[1].lower()
    return ext[1:] if ext.startswith(".") else ext


def _group_by_extension(paths: List[str]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for p in paths:
        e = _ext_of(p)
        grouped.setdefault(e, []).append(p)
    return grouped


def _shallow_cover_for_ext(paths: List[str]) -> List[str]:
    # Return minimal set of umbrella patterns covering all provided relative paths of the same extension.
    # Strategy:
    # - If only one file: return the file path as-is (exact match)
    # - Otherwise, try to find shallow directory buckets:
    #   1) If all files live directly under the same directory D -> D/*.ext
    #   2) If all files live under a common ancestor A (at any depth) -> A/**/*.<ext>
    #   3) Else, partition by top-level directory and repeat per group; if a file is at repo root, include *.ext
    if not paths:
        return []

    if len(paths) == 1:
        return [paths[0]]

    # Compute extension once
    ext = _ext_of(paths[0])

    # Extract directory parts for each path
    dir_parts: List[List[str]] = [ _split_path(os.path.dirname(p)) for p in paths ]

    # Helper: find common prefix length among lists
    def common_prefix_length(seqs: List[List[str]]) -> int:
        if not seqs:
            return 0
        min_len = min(len(s) for s in seqs)
        k = 0
        while k < min_len:
            token = seqs[0][k]
            if all(s[k] == token for s in seqs):
                k += 1
            else:
                break
        return k

    # Case: all under same parent directory exactly
    all_same_parent = len({ "/".join(d) for d in dir_parts }) == 1
    if all_same_parent:
        parent = "/".join(dir_parts[0])
        if parent:
            return [f"{parent}/*.{ext}"]
        # all at repo root
        return [f"*.{ext}"]

    # Case: share a common ancestor A at depth > 0
    cpl = common_prefix_length(dir_parts)
    if cpl > 0:
        ancestor = "/".join(dir_parts[0][:cpl])
        return [f"{ancestor}/**/*.{ext}"]

    # Otherwise, partition by top-level folder (first component) or root
    buckets: Dict[str, List[str]] = {}
    for path, parts in zip(paths, dir_parts):
        top = parts[0] if parts else ""
        buckets.setdefault(top, []).append(path)

    patterns: List[str] = []
    for top, group in buckets.items():
        if top == "":
            # some files at root
            # if group has only root files -> *.ext else fallback to **
            only_root = all(os.path.dirname(p) == "" for p in group)
            if only_root:
                patterns.append(f"*.{ext}")
            else:
                patterns.append(f"**/*.{ext}")
        else:
            # recurse shallowly within this bucket
            # Derive subpatterns but make them relative to 'top'
            sub_dirs = [ p[len(top)+1:] for p in group ]
            sub = _shallow_cover_for_ext(sub_dirs)
            for pat in sub:
                if pat.startswith("**/") or pat.startswith("*."):
                    patterns.append(f"{top}/{pat}")
                elif pat.startswith(top+"/"):
                    patterns.append(pat)
                else:
                    patterns.append(f"{top}/{pat}")
    return patterns


def compute_minimal_left_patterns(included_paths: List[str]) -> List[str]:
    grouped = _group_by_extension(included_paths)
    suggestions: List[str] = []
    for ext, paths in sorted(grouped.items()):
        if ext == "":
            # no extension; list exact files
            for p in sorted(paths):
                suggestions.append(p)
            continue
        # make patterns for this ext
        patterns = _shallow_cover_for_ext(sorted(paths))
        suggestions.extend(patterns)
    # dedupe while preserving order
    seen: Set[str] = set()
    result: List[str] = []
    for p in suggestions:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


