"""Tree plotting and ASCII visualization."""

from typing import List, Optional
from projectsummarizer.files.tree.node import FsNode


class TreePlotter:
    """Plots filesystem trees in various formats."""
    
    def __init__(self):
        """Initialize the tree plotter."""
        pass
    
    def plot_ascii(self, root: FsNode) -> str:
        """Plot tree in ASCII format with statistics.
        
        Args:
            root: Root node of the tree to plot
            
        Returns:
            ASCII tree representation as string
        """
        lines: List[str] = []

        def format_stats(node: FsNode) -> str:
            """Format statistics for a node using its own stats."""
            node_stats = node.stats()
            if not node_stats:
                return ""
            
            parts = []
            for stat_name, stat_value in node_stats.items():
                if stat_name == "size":
                    parts.append(f"{stat_value}B")
                else:
                    parts.append(f"{stat_name}:{stat_value}")
            
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


