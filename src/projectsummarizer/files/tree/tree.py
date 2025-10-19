import os
from typing import Dict
from projectsummarizer.files.tree.node import FileSystemNode


class FileSystemTree:
    """Builds a filesystem tree structure from files metadata.

    This class is responsible for ONLY building tree structures from existing
    file metadata. It does NOT perform file I/O or discovery - that's the job
    of FileDiscoverer.

    Responsibilities:
    - Parse file paths into tree hierarchy
    - Create FileSystemNode instances
    - Build parent-child relationships
    - Compute aggregate metrics (sizes, token counts)

    Not responsible for:
    - File system traversal (use FileDiscoverer)
    - Reading files (use FileDiscoverer)
    - Ignore patterns (use FileDiscoverer)
    - Binary detection (use FileDiscoverer)
    """

    @staticmethod
    def extract_path_parts(relative_path: str) -> list[str]:
        """Extract path parts from a relative path.

        Args:
            relative_path: Path like "dir/subdir/file.py"

        Returns:
            List of path components: ["dir", "subdir", "file.py"]
        """
        return relative_path.split("/") if relative_path else []

    @staticmethod
    def extract_extension(relative_path: str) -> str:
        """Extract file extension from a relative path.

        Args:
            relative_path: Path like "dir/file.py" or ".gitignore"

        Returns:
            Extension without dot in lowercase: "py", "gitignore"
        """
        basename = os.path.basename(relative_path)
        # Handle dotfiles like .gitignore (extension is everything after the dot)
        if basename.startswith(".") and basename.count(".") == 1:
            return basename[1:].lower()
        # Normal files: extract extension
        _, extension = os.path.splitext(basename)
        return extension[1:].lower() if extension.startswith(".") else ""

    def __init__(self, files_data: Dict[str, Dict]) -> None:
        """Build a filesystem tree from files metadata.

        Args:
            files_data: Dictionary mapping relative paths to file metadata.
                       Expected format: {
                           "path/to/file.py": {
                               "size": 1024,
                               "tokens": {"gpt-4o": 256},
                               "flags": {"binary"}
                           }
                       }

        Example:
            >>> from projectsummarizer import FileDiscoverer, FileSystemTree
            >>> discoverer = FileDiscoverer(root="./src")
            >>> files_data = discoverer.discover()
            >>> tree = FileSystemTree(files_data)
            >>> print(tree.root.size)
        """
        # Build root node
        root_node = FileSystemNode(name="", is_directory=True, relative_path="")
        index: Dict[str, FileSystemNode] = {"": root_node}

        # Build tree structure from file paths
        for relative_path, data in files_data.items():
            parent = root_node
            current_path = ""
            path_parts = self.extract_path_parts(relative_path)

            # Create intermediate directory nodes and final file node
            for i, part in enumerate(path_parts):
                current_path = f"{current_path}/{part}" if current_path else part
                node = index.get(current_path)
                is_directory = i < len(path_parts) - 1

                if node is None:
                    node = FileSystemNode(
                        name=part,
                        is_directory=is_directory,
                        relative_path=current_path,
                        parent=parent
                    )
                    index[current_path] = node
                parent = node

            # Set file metadata on the leaf node
            file_node = index[current_path]
            file_node.extension = self.extract_extension(relative_path)
            file_node.set_file_metrics(
                size=data.get("size", 0),
                tokens=data.get("tokens", {})
            )
            for flag in data.get("flags", set()):
                file_node.mark_flag(flag)

        # Compute aggregate metrics for all directories
        root_node.recompute_aggregates()
        self.root = root_node

