from typing import Dict, Optional, Set, List
from anytree import NodeMixin, PostOrderIter, PreOrderIter


class FileSystemNode(NodeMixin):
    """Filesystem tree node with metrics and lazy aggregates.

    This class is designed for extension: override hooks or add methods
    without changing its construction API.
    """

    def __init__(
        self,
        name: str,
        *,
        is_directory: bool = False,
        relative_path: str = "",
        extension: str = "",
        parent: Optional["FileSystemNode"] = None,
    ) -> None:
        self.name = name
        self.is_directory = is_directory
        self.relative_path = relative_path
        self.extension = extension
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
        if not self.is_directory:
            return self._file_size
        if self._dirty:
            self._recompute_aggregates_for_node()
        return self._agg_size

    @property
    def tokens(self) -> Dict[str, int]:
        if not self.is_directory:
            return self._file_tokens
        if self._dirty:
            self._recompute_aggregates_for_node()
        return self._agg_tokens

    def set_file_metrics(self, *, size: Optional[int] = None, tokens: Optional[Dict[str, int]] = None) -> None:
        if self.is_directory:
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
        node: Optional["FileSystemNode"] = self
        while node is not None:
            node._dirty = True
            node = node.parent

    def recompute_aggregates(self) -> None:
        for node in PostOrderIter(self):
            if node.is_directory:
                node._recompute_aggregates_for_node()

    def _recompute_aggregates_for_node(self) -> None:
        """Recompute all aggregate metrics for a directory node.

        Aggregates include:
        - size: sum of children's sizes
        - tokens: key-wise sum of children's token dicts
        """
        # Aggregate sizes
        self._agg_size = sum(child.size for child in self.children)

        # Aggregate token counts by key
        aggregated: Dict[str, int] = {}
        for child in self.children:
            for key, value in (child.tokens or {}).items():
                aggregated[key] = aggregated.get(key, 0) + int(value)
        self._agg_tokens = aggregated

        self._dirty = False

    def get_file_paths(self) -> List[str]:
        """Get all file paths in this tree (excluding directories)."""
        return [node.relative_path for node in PreOrderIter(self)
                if not node.is_directory and node.relative_path]

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
        kind = "directory" if self.is_directory else "file"
        return f"FileSystemNode({kind} {self.relative_path or '.'}, size={self.size})"

