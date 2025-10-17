import os
from typing import Dict, Iterable, List, Optional
from projectsummarizer.files.tree.node import FsNode
from projectsummarizer.tokens.counter import TokenCounter
    


def _parts(rel: str) -> List[str]:
    return rel.split("/") if rel else []


def _ext_of(rel: str) -> str:
    base = os.path.basename(rel)
    if base.startswith(".") and base.count(".") == 1:
        return base[1:].lower()
    _, ext = os.path.splitext(base)
    return ext[1:].lower() if ext.startswith(".") else ""


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
        relpaths: Iterable[str], 
        token_counter: Optional["TokenCounter"] = None
    ) -> Dict[str, Dict]:
        """Gather file sizes and optional token counts for the given relative paths."""
        out: Dict[str, Dict] = {}
        for rel in relpaths:
            full = os.path.join(directory, rel)
            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0
            
            meta = {"size": int(size), "flags": set()}
            
            # Add token counts if token_counter is provided
            if token_counter:
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        content = f.read()
                    tokens = token_counter.count_tokens(content)
                    meta["tokens"] = tokens
                except (OSError, UnicodeDecodeError):
                    meta["tokens"] = {}
            
            out[rel] = meta
        return out


    @property
    def root(self) -> FsNode:
        return self._root

    def _build(self, files_data: Dict[str, Dict]) -> FsNode:
        root = FsNode(name="", is_dir=True, relpath="")
        index: Dict[str, FsNode] = {"": root}

        for rel, data in files_data.items():
            parent = root
            cur = ""
            parts = _parts(rel)
            for i, part in enumerate(parts):
                cur = f"{cur}/{part}" if cur else part
                node = index.get(cur)
                is_dir = i < len(parts) - 1
                if node is None:
                    node = FsNode(name=part, is_dir=is_dir, relpath=cur, parent=parent)
                    index[cur] = node
                parent = node

            file_node = index[cur]
            file_node.ext = _ext_of(rel)
            file_node.set_file_metrics(
                size=data.get("size", 0),
                tokens=data.get("tokens", {})
            )
            for flag in data.get("flags", set()):
                file_node.mark_flag(flag)

        root.recompute_aggregates()
        return root


def build_fs_tree(files_data: Dict[str, Dict]) -> FsNode:
    return FileSystemTree(files_data).root

