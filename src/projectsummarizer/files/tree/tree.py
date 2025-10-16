import os
from typing import Dict, Iterable, List, Optional
from .node import FsNode
from ...tokens.counter import TokenCounter
    


def _parts(rel: str) -> List[str]:
    return rel.split("/") if rel else []


def _ext_of(rel: str) -> str:
    base = os.path.basename(rel)
    if base.startswith(".") and base.count(".") == 1:
        return base[1:].lower()
    _, ext = os.path.splitext(base)
    return ext[1:].lower() if ext.startswith(".") else ""


class FileSystemTree:
    """Builds and renders a filesystem tree from relative paths and metadata."""

    def __init__(self, relpaths: Iterable[str], per_file_meta: Dict[str, Dict]) -> None:
        self._root = self._build(relpaths, per_file_meta)

    @classmethod
    def from_directory(
        cls, 
        directory: str, 
        relpaths: Iterable[str], 
        token_counter: Optional["TokenCounter"] = None
    ) -> "FileSystemTree":
        """Create a FileSystemTree from a directory and relative paths, gathering file sizes and optional token counts."""
        meta = cls._gather_file_metadata(directory, relpaths, token_counter)
        return cls(relpaths, meta)

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

    def _build(self, relpaths: Iterable[str], per_file_meta: Dict[str, Dict]) -> FsNode:
        root = FsNode(name="", is_dir=True, relpath="")
        index: Dict[str, FsNode] = {"": root}

        for rel in relpaths:
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
            meta = per_file_meta.get(rel, {})
            file_node.set_file_metrics(
                size=meta.get("size", 0),
                tokens=meta.get("tokens", {})
            )
            for flag in meta.get("flags", set()):
                file_node.mark_flag(flag)

        root.recompute_aggregates()
        return root


# Tree plotting functionality moved to plotting module
# Use: from projectsummarizer.plotting import ascii_tree


def build_fs_tree(relpaths: Iterable[str], per_file_meta: Dict[str, Dict]) -> FsNode:
    return FileSystemTree(relpaths, per_file_meta).root

