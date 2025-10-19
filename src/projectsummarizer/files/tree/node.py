from typing import Dict, Optional, Set, List
from anytree import NodeMixin, PostOrderIter, PreOrderIter


class FileSystemNode(NodeMixin):
    """Filesystem tree node with metrics and lazy aggregate computation.

    This class represents a single node (file or directory) in the filesystem tree.
    It uses the anytree library for tree structure and relationships.

    Responsibilities:
    - Store node data (name, path, extension, flags)
    - Store file metrics (size, token counts)
    - Compute and cache aggregate metrics for directories
    - Provide tree traversal via anytree (children, parent, etc.)
    - Track dirty state for efficient recomputation

    Key features:
    - Lazy aggregation: Directory metrics computed on first access
    - Dirty flag: Only recomputes when children change
    - Extensible: Can override hooks or add methods

    Not responsible for:
    - File discovery (use FileDiscoverer)
    - Tree building (use FileSystemTree)
    - File I/O (use FileDiscoverer)
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
        self.file_size: int = 0
        self.file_tokens: Dict[str, int] = {}
        self.aggregate_size: int = 0
        self.aggregate_tokens: Dict[str, int] = {}
        self.dirty: bool = True

    # ---- metrics ----
    @property
    def size(self) -> int:
        if not self.is_directory:
            return self.file_size
        if self.dirty:
            self.recompute_aggregates_for_node()
        return self.aggregate_size

    @property
    def tokens(self) -> Dict[str, int]:
        if not self.is_directory:
            return self.file_tokens
        if self.dirty:
            self.recompute_aggregates_for_node()
        return self.aggregate_tokens

    def set_file_metrics(self, *, size: Optional[int] = None, tokens: Optional[Dict[str, int]] = None) -> None:
        """Set metrics for a file node.

        Args:
            size: File size in bytes
            tokens: Token counts by model name

        Raises:
            ValueError: If called on a directory node
        """
        if self.is_directory:
            raise ValueError("set_file_metrics() only valid for files")
        if size is not None:
            self.file_size = int(size)
        if tokens is not None:
            self.file_tokens = {k: int(v) for k, v in (tokens or {}).items()}
        self.mark_dirty_up()

    def mark_flag(self, flag: str) -> None:
        """Mark this node with a flag (e.g., 'binary').

        Args:
            flag: Flag name to add
        """
        self.flags.add(flag)
        self.mark_dirty_up()

    # ---- maintenance ----
    def mark_dirty_up(self) -> None:
        """Mark this node and all ancestors as needing recomputation.

        This is called when a node's data changes, so that aggregate
        metrics will be recalculated on next access.
        """
        node: Optional["FileSystemNode"] = self
        while node is not None:
            node.dirty = True
            node = node.parent

    def recompute_aggregates(self) -> None:
        """Recompute all aggregate metrics for all directory nodes in tree."""
        for node in PostOrderIter(self):
            if node.is_directory:
                node.recompute_aggregates_for_node()

    def recompute_aggregates_for_node(self) -> None:
        """Recompute aggregate metrics for this directory node.

        Aggregates include:
        - size: sum of children's sizes
        - tokens: key-wise sum of children's token dicts

        This is called automatically when accessing size/tokens on a dirty directory.
        """
        # Aggregate sizes
        self.aggregate_size = sum(child.size for child in self.children)

        # Aggregate token counts by key
        aggregated: Dict[str, int] = {}
        for child in self.children:
            for key, value in (child.tokens or {}).items():
                aggregated[key] = aggregated.get(key, 0) + int(value)
        self.aggregate_tokens = aggregated

        self.dirty = False

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

