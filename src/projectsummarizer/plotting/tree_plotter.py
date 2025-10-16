"""Tree plotting and ASCII visualization."""

from typing import List, Optional
from ..files.tree.node import FsNode


class TreePlotter:
    """Plots filesystem trees in various formats."""
    
    def __init__(self, show_stats: List[str] | None = None):
        """Initialize with optional statistics to display.
        
        Args:
            show_stats: List of stat names to display (e.g., ['size', 'gpt-4o'])
                       If None, shows only size. If empty, shows no stats.
        """
        self.show_stats = show_stats
    
    def plot_ascii(self, root: FsNode) -> str:
        """Plot tree in ASCII format with statistics.
        
        Args:
            root: Root node of the tree to plot
            
        Returns:
            ASCII tree representation as string
        """
        lines: List[str] = []

        def format_stats(node: FsNode) -> str:
            """Format statistics for a node."""
            if self.show_stats is None:
                # Default: show only size
                return f" ({node.size}B)"
            elif not self.show_stats:
                # Empty list: show no stats
                return ""
            else:
                # Show specified stats
                node_stats = node.stats()
                parts = []
                for stat in self.show_stats:
                    if stat in node_stats:
                        if stat == "size":
                            parts.append(f"{node_stats[stat]}B")
                        else:
                            parts.append(f"{stat}:{node_stats[stat]}")
                return " (" + "; ".join(parts) + ")" if parts else ""

        def walk(node: FsNode, prefix: str = ""):
            kids = sorted(node.children, key=lambda x: (not x.is_dir, x.name.lower()))
            for i, c in enumerate(kids):
                is_last = i == len(kids) - 1
                branch = "└── " if is_last else "├── "
                
                # Format node name and stats
                node_name = c.name + ("/" if c.is_dir else "")
                stats = format_stats(c)
                lines.append(prefix + branch + node_name + stats)
                
                if c.is_dir:
                    extend = "    " if is_last else "│   "
                    walk(c, prefix + extend)

        # Root node
        root_name = "."
        root_stats = format_stats(root)
        lines.append(root_name + root_stats)
        
        # Children
        walk(root, "")
        return "\n".join(lines)


