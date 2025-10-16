from typing import Dict, Optional, Set, List
from anytree import NodeMixin, PostOrderIter, PreOrderIter


class FsNode(NodeMixin):
    """Filesystem tree node with metrics and lazy aggregates.

    This class is designed for extension: override hooks or add methods
    without changing its construction API.
    """

    def __init__(
        self,
        name: str,
        *,
        is_dir: bool = False,
        relpath: str = "",
        ext: str = "",
        parent: Optional["FsNode"] = None,
    ) -> None:
        self.name = name
        self.is_dir = is_dir
        self.relpath = relpath
        self.ext = ext
        self.parent = parent

        self.flags: Set[str] = set()
        self._file_size: int = 0
        self._file_tokens: Dict[str, int] = {}
        self._agg_size: int = 0
        self._agg_tokens: Dict[str, int] = {}
        self._dirty: bool = True

    # ---- metrics ----
    @property
    def size(self) -> int:
        if not self.is_dir:
            return self._file_size
        if self._dirty:
            self._agg_size = sum(c.size for c in self.children)
            self._dirty = False
        return self._agg_size

    @property
    def tokens(self) -> Dict[str, int]:
        return self._file_tokens if not self.is_dir else self._agg_tokens

    def set_file_metrics(self, *, size: Optional[int] = None, tokens: Optional[Dict[str, int]] = None) -> None:
        if self.is_dir:
            raise ValueError("set_file_metrics() only valid for files")
        if size is not None:
            self._file_size = int(size)
        if tokens is not None:
            self._file_tokens = {k: int(v) for k, v in (tokens or {}).items()}
        self._mark_dirty_up()

    def mark_flag(self, flag: str) -> None:
        self.flags.add(flag)
        self._mark_dirty_up()

    # ---- maintenance ----
    def _mark_dirty_up(self) -> None:
        n: Optional["FsNode"] = self
        while n is not None:
            n._dirty = True
            n = n.parent

    def recompute_aggregates(self) -> None:
        for n in PostOrderIter(self):
            if n.is_dir:
                n._agg_size = sum(c.size for c in n.children)
                n._agg_tokens = {}
                n._dirty = False

    def get_file_paths(self) -> List[str]:
        """Get all file paths in this tree (excluding directories)."""
        return [node.relpath for node in PreOrderIter(self) 
                if not node.is_dir and node.relpath]

    def stats(self) -> Dict[str, int]:
        """Get statistics for this node as a dictionary.
        
        Returns:
            Dictionary with 'size' and any available token counts
        """
        stats_dict = {"size": self.size}
        if self.tokens:
            stats_dict.update(self.tokens)
        return stats_dict

    # ---- debugging ----
    def __repr__(self) -> str:
        kind = "dir" if self.is_dir else "file"
        return f"FsNode({kind} {self.relpath or '.'}, size={self.size})"

