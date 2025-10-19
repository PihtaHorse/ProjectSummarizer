"""Tree plotting and ASCII visualization."""

from typing import List
from projectsummarizer.files.tree.node import FileSystemNode


class TreePlotter:
    """Plots filesystem trees in various formats."""

    def plot_ascii(self, root: FileSystemNode) -> str:
        """Plot tree in ASCII format with statistics.

        Args:
            root: Root node of the tree to plot

        Returns:
            ASCII tree representation as string
        """
        lines: List[str] = []

        def format_stats(node: FileSystemNode) -> str:
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

        def walk(node: FileSystemNode, prefix: str = ""):
            children = sorted(node.children, key=lambda child: (not child.is_directory, child.name.lower()))
            for index, child in enumerate(children):
                is_last = index == len(children) - 1
                branch = "└── " if is_last else "├── "

                # Format node name and stats
                node_name = child.name + ("/" if child.is_directory else "")
                stats = format_stats(child)
                lines.append(prefix + branch + node_name + stats)

                if child.is_directory:
                    extend = "    " if is_last else "│   "
                    walk(child, prefix + extend)

        # Root node
        root_name = "."
        root_stats = format_stats(root)
        lines.append(root_name + root_stats)

        # Children
        walk(root, "")
        return "\n".join(lines)


