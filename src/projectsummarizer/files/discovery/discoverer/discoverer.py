import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
from projectsummarizer.files.discovery.ignore import IgnorePatternsHandler
from projectsummarizer.files.discovery.binary_detector import BinaryDetector
from projectsummarizer.files.discovery.discoverer.date_time_mixin import DateTimeMixin
from projectsummarizer.contents.readers import ContentReaderRegistry, NotebookReader, BinaryFileReader, TextFileReader


class FileDiscoverer(DateTimeMixin):
    """Discovers files and gathers their metadata from a directory tree.

    This class is responsible for ALL file system I/O and metadata collection.
    It does NOT build tree structures - that's the job of FileSystemTree.

    Responsibilities:
    - Walk directory tree (file system traversal)
    - Apply ignore patterns (via IgnorePatternsHandler)
    - Detect binary files
    - Gather file sizes
    - Read files and count tokens (if token_counter provided)
    - Return flat dictionary of file metadata

    Not responsible for:
    - Building tree structures (use FileSystemTree)
    - Tree node creation (use FileSystemTree)
    - Computing aggregate metrics (use FileSystemTree)

    The output of this class is meant to be consumed by FileSystemTree constructor.
    """

    def __init__(
        self,
        root: str,
        *,
        user_patterns: List[str] = None,
        use_defaults: bool = True,
        read_ignore_files: bool = True,
        include_binary: bool = False,
        binary_detector: Optional[BinaryDetector] = None,
        token_counter = None,
        filter_type: str = "included",
        level: Optional[int] = None,
        include_dates: bool = False
    ) -> None:
        self.root = Path(root)
        self.token_counter = token_counter
        self.filter_type = filter_type
        self.level = level
        self.include_dates = include_dates

        # Check if we're in a git repository
        self._is_git_repo_cached = None

        # Create the centralized ignore handler
        self.ignore_handler = IgnorePatternsHandler(
            root=root,
            user=user_patterns or [],
            use_defaults=use_defaults,
            read_ignore_files=read_ignore_files,
            include_binary=include_binary,
            binary_detector=binary_detector
        )

        # Initialize content reader registry and register readers
        # Order matters: more specific readers first, fallback last
        self.content_registry = ContentReaderRegistry()
        self.content_registry.register(NotebookReader())
        self.content_registry.register(BinaryFileReader())
        self.content_registry.register(TextFileReader())  # Fallback reader

    def discover(self, content_processor: Optional[Callable[[str, str], None]] = None) -> Dict[str, Dict]:
        """Discover files and optionally process their content via a callback.

        This method reads each file exactly once and allows streaming processing
        of file contents without storing all content in memory.

        Args:
            content_processor: Optional callback function(relative_path, content)
                             called for each non-binary file after reading.
                             If None, files are still read for token counting if token_counter is set.

        Returns:
            Dictionary mapping relative paths to file metadata containing:
            - is_binary: bool - whether the file is binary
            - size: int - file size in bytes
            - flags: set - file flags (e.g., 'binary')
            - tokens: dict - token counts (if token_counter provided)

        Filter types:
        - "included": files that pass ignore patterns (default)
        - "removed": files that are ignored by patterns
        - "all": all files regardless of ignore patterns

        Example:
            # Without callback (just gather metadata)
            files_data = discoverer.discover()

            # With callback (stream content)
            def write_content(path, content):
                output_file.write(f"\\n### {path}\\n{content}\\n")
            files_data = discoverer.discover(write_content)
        """
        files_data: Dict[str, Dict] = {}
        for current_directory, _, files in os.walk(self.root, topdown=True):
            for filename in files:
                relative_path = (Path(current_directory) / filename).relative_to(self.root).as_posix()
                full_path = (Path(current_directory) / filename).as_posix()

                # Check level limit if specified
                if self.level is not None:
                    # Calculate level by counting path separators
                    # Root directory files have level 0
                    depth = len(Path(relative_path).parts) - 1
                    if depth > self.level:
                        continue

                # Use centralized ignore logic
                ignore_data = self.ignore_handler.is_ignored(relative_path, full_path)

                # Apply filter logic
                should_include = self.should_include_file(ignore_data["is_ignored"])
                if not should_include:
                    continue

                # Get file size
                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                # Prepare file data
                file_data = {
                    "is_binary": ignore_data["is_binary"],
                    "size": size,
                    "flags": set()
                }

                # Add binary flag if present
                if ignore_data["is_binary"]:
                    file_data["flags"].add("binary")

                # Read file using the content reader registry
                # This properly handles notebooks, binary files, and text files
                content = self.content_registry.read(full_path, file_data=file_data)

                # Add token counts if token_counter is provided and content was read
                if self.token_counter and content:
                    tokens = self.token_counter.count_tokens(content)
                    file_data["tokens"] = tokens
                else:
                    file_data["tokens"] = {}

                # Add file dates if requested
                if self.include_dates:
                    created, modified = self._get_file_dates(full_path)
                    if created:
                        file_data["created"] = created
                    if modified:
                        file_data["modified"] = modified

                # Call content processor if provided and content was read
                if content_processor and content:
                    content_processor(relative_path, content)

                files_data[relative_path] = file_data

        return files_data

    def should_include_file(self, is_ignored: bool) -> bool:
        """Determine if a file should be included based on filter type."""
        if self.filter_type == "all":
            return True
        elif self.filter_type == "removed":
            return is_ignored
        else:  # "included" (default)
            return not is_ignored

