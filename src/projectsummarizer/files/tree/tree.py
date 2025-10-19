import os
from typing import Dict, Iterable, List, Optional
from projectsummarizer.files.tree.node import FileSystemNode
from projectsummarizer.tokens.counter import TokenCounter



def _extract_path_parts(relative_path: str) -> List[str]:
    """Extract path parts from a relative path."""
    return relative_path.split("/") if relative_path else []


def _extract_extension(relative_path: str) -> str:
    """Extract file extension from a relative path."""
    basename = os.path.basename(relative_path)
    if basename.startswith(".") and basename.count(".") == 1:
        return basename[1:].lower()
    _, extension = os.path.splitext(basename)
    return extension[1:].lower() if extension.startswith(".") else ""


class FileSystemTree:
    """Builds and renders a filesystem tree from files data."""

    def __init__(self, files_data: Dict[str, Dict]) -> None:
        self._root = self._build(files_data)

    @classmethod
    def from_files_data(
        cls, 
        files_data: Dict[str, Dict]
    ) -> "FileSystemTree":
        """Create a FileSystemTree from files data."""
        return cls(files_data)

    @classmethod
    def from_directory(
        cls, 
        directory: str, 
        relpaths: Iterable[str], 
        token_counter: Optional["TokenCounter"] = None,
        files_data: Optional[Dict[str, Dict]] = None
    ) -> "FileSystemTree":
        """Create a FileSystemTree from a directory and relative paths, gathering file sizes and optional token counts."""
        if files_data is not None:
            # Use provided files data as-is
            return cls(files_data)
        else:
            # Fallback to gathering metadata from scratch
            meta = cls._gather_file_metadata(directory, relpaths, token_counter)
            return cls(meta)

    @staticmethod
    def _gather_file_metadata(
        directory: str,
        relative_paths: Iterable[str],
        token_counter: Optional["TokenCounter"] = None
    ) -> Dict[str, Dict]:
        """Gather file sizes and optional token counts for the given relative paths."""
        files_metadata: Dict[str, Dict] = {}
        for relative_path in relative_paths:
            full_path = os.path.join(directory, relative_path)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0

            metadata = {"size": int(size), "flags": set()}

            # Add token counts if token_counter is provided
            if token_counter:
                try:
                    with open(full_path, "r", encoding="utf-8") as file:
                        content = file.read()
                    tokens = token_counter.count_tokens(content)
                    metadata["tokens"] = tokens
                except (OSError, UnicodeDecodeError):
                    metadata["tokens"] = {}

            files_metadata[relative_path] = metadata
        return files_metadata


    @property
    def root(self) -> FileSystemNode:
        return self._root

    def _build(self, files_data: Dict[str, Dict]) -> FileSystemNode:
        root = FileSystemNode(name="", is_directory=True, relative_path="")
        index: Dict[str, FileSystemNode] = {"": root}

        for relative_path, data in files_data.items():
            parent = root
            current_path = ""
            path_parts = _extract_path_parts(relative_path)
            for i, part in enumerate(path_parts):
                current_path = f"{current_path}/{part}" if current_path else part
                node = index.get(current_path)
                is_directory = i < len(path_parts) - 1
                if node is None:
                    node = FileSystemNode(name=part, is_directory=is_directory, relative_path=current_path, parent=parent)
                    index[current_path] = node
                parent = node

            file_node = index[current_path]
            file_node.extension = _extract_extension(relative_path)
            file_node.set_file_metrics(
                size=data.get("size", 0),
                tokens=data.get("tokens", {})
            )
            for flag in data.get("flags", set()):
                file_node.mark_flag(flag)

        root.recompute_aggregates()
        return root


def build_filesystem_tree(files_data: Dict[str, Dict]) -> FileSystemNode:
    """Build a filesystem tree from files data dictionary."""
    return FileSystemTree(files_data).root

