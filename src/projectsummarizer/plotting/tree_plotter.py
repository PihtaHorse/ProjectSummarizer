"""Tree plotting and ASCII visualization."""

from typing import List
from projectsummarizer.files.tree.node import FileSystemNode


class TreePlotter:
    """Plots filesystem trees in various formats."""

    @staticmethod
    def format_size(bytes_value: int) -> str:
        """Convert bytes to human-readable format.

        Args:
            bytes_value: Size in bytes

        Returns:
            Human-readable size string (e.g., "1.24 KB", "15.67 MB")

        Examples:
            >>> TreePlotter.format_size(0)
            '0.00 B'
            >>> TreePlotter.format_size(1024)
            '1.00 KB'
            >>> TreePlotter.format_size(1048576)
            '1.00 MB'
            >>> TreePlotter.format_size(1536)
            '1.50 KB'
        """
        bytes_float = float(bytes_value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_float < 1024.0 or unit == "TB":
                return f"{bytes_float:.2f} {unit}"
            bytes_float /= 1024.0
        return f"{bytes_float:.2f} TB"

    def plot_ascii(
        self,
        root: FileSystemNode,
        show_stats: bool = True,
        sort_by: str = "name"
    ) -> str:
        """Plot tree in ASCII format with optional statistics and sorting.

        Args:
            root: Root node of the tree to plot
            show_stats: Whether to show statistics (size, tokens). Default: True
            sort_by: Sort children by 'name' (default), 'size', or any token model name

        Returns:
            ASCII tree representation as string
        """
        lines: List[str] = []

        def format_stats(node: FileSystemNode) -> str:
            """Format statistics for a node using its own stats."""
            if not show_stats:
                return ""

            node_stats = node.stats()
            if not node_stats:
                return ""

            parts = []
            for stat_name, stat_value in node_stats.items():
                if stat_name == "size":
                    parts.append(TreePlotter.format_size(stat_value))
                elif stat_name in ["created", "modified"]:
                    parts.append(f"{stat_name}: {stat_value}")
                else:
                    parts.append(f"{stat_name}:{stat_value}")

            return " (" + "; ".join(parts) + ")" if parts else ""

        def walk(node: FileSystemNode, prefix: str = ""):
            # Define sorting key based on sort_by parameter
            def sort_key(child: FileSystemNode):
                # Always sort directories before files
                is_file = not child.is_directory

                if sort_by == "name":
                    return (is_file, child.name.lower())
                elif sort_by == "size":
                    # Sort by size descending (negate for reverse), then by name
                    return (is_file, -child.size, child.name.lower())
                elif sort_by == "created":
                    # Sort by created date, newest first (descending)
                    # Use low date value for None to sort them to end
                    # Negate by using reverse=True in sorted() or by string reversal trick
                    date_value = child.created if child.created else "0000-00-00"
                    # Reverse the date string for descending sort (newer dates = higher strings reversed = lower)
                    # Instead, we'll negate after: return tuple with negative comparison
                    return (not is_file, date_value, child.name.lower())
                elif sort_by == "modified":
                    # Sort by modified date, newest first (descending)
                    # Use low date value for None to sort them to end
                    date_value = child.modified if child.modified else "0000-00-00"
                    return (not is_file, date_value, child.name.lower())
                else:
                    # Treat sort_by as a token model name
                    token_count = child.tokens.get(sort_by, 0) if child.tokens else 0
                    return (is_file, -token_count, child.name.lower())

            # Sort with reverse=True for date sorting to get newest first
            # This preserves the directories-first ordering from is_file in the sort key
            if sort_by in ["created", "modified"]:
                children = sorted(node.children, key=sort_key, reverse=True)
            else:
                children = sorted(node.children, key=sort_key)
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


