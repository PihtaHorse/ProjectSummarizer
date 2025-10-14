import os
import fnmatch
from typing import List

IGNORE_FILES = [".gitignore", ".dockerignore"]


def parse_ignore_files(directory: str) -> List[str]:
    ignore_patterns: List[str] = []
    for ignore_file in IGNORE_FILES:
        ignore_path = os.path.join(directory, ignore_file)
        if os.path.exists(ignore_path):
            with open(ignore_path, "r", encoding="utf-8") as file:
                ignore_patterns.extend(
                    line.strip()
                    for line in file
                    if line.strip() and not line.startswith("#")
                )
    return ignore_patterns


def should_ignore(file_path: str, top_level_dir: str, ignore_patterns: List[str]) -> bool:
    # Always compute relative paths from the top-level directory
    relative_path = os.path.relpath(file_path, top_level_dir).replace(os.sep, "/")
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(relative_path, pattern):
            return True
    return False


def collect_file_paths(
    directory: str,
    global_ignore_patterns: List[str],
    include_ignore_files: bool = True,
) -> List[str]:
    file_paths: List[str] = []
    # Pre-parse ignore files from the top-level directory
    top_level_ignore_patterns = list(global_ignore_patterns)
    if include_ignore_files:
        top_level_ignore_patterns += parse_ignore_files(directory)

    for root, dirs, files in os.walk(directory, topdown=True):
        # Combine top-level patterns with local ignore files from the current root
        local_ignore_patterns = list(top_level_ignore_patterns)
        if include_ignore_files:
            local_ignore_patterns += parse_ignore_files(root)
        # Filter directories
        dirs[:] = [
            d
            for d in dirs
            if not should_ignore(os.path.join(root, d), directory, local_ignore_patterns)
        ]
        # Filter files
        for name in files:
            file_path = os.path.join(root, name)
            if not should_ignore(file_path, directory, local_ignore_patterns):
                rel_path = os.path.relpath(file_path, directory).replace(os.sep, "/")
                file_paths.append(rel_path)
    return file_paths


