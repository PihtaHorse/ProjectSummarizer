"""Heuristic-based binary file detector as fallback when libmagic is unavailable."""

import os
from projectsummarizer.files.discovery.binary_detectors.binary_extensions import BINARY_EXTENSIONS


class HeuristicBinaryDetector:
    """Heuristic-based binary detector without libmagic dependency.

    Uses multiple heuristics to detect binary files:
    1. Check file extension against known binary formats (blacklist)
    2. Check for null bytes (strong indicator of binary)
    3. Try UTF-8 decoding
    4. Analyze ratio of printable to non-printable characters

    When uncertain, prefers to treat files as text (false negatives over false positives).
    This is appropriate for a project summarizer where including questionable content
    is better than excluding valid text files.
    """

    def __init__(self) -> None:
        self._binary_extensions = BINARY_EXTENSIONS

    def is_binary(self, path: str, sample_bytes: int = 65536) -> bool:
        """Return True if the file at `path` should be treated as binary."""
        try:
            with open(path, "rb", buffering=0) as f:
                head = f.read(sample_bytes)
        except Exception:
            # If we can't read the file, treat it as binary (conservative)
            return True

        return self._is_binary_data(head, path)

    def _is_binary_data(self, data: bytes, path: str = "") -> bool:
        """Check if data should be treated as binary using heuristics.

        When uncertain, prefers to treat files as text (false negatives over false positives).
        """
        # Check file extension against blacklist
        if path:
            _, ext = os.path.splitext(path)
            if ext.lower() in self._binary_extensions:
                return True

        # Empty data is not binary
        if not data:
            return False

        # Check for null bytes - strong indicator of binary
        if b'\x00' in data:
            return True

        # Try to decode as UTF-8
        try:
            data.decode('utf-8')
            # Successfully decoded as UTF-8, treat as text
            return False
        except UnicodeDecodeError:
            # Failed UTF-8 decoding, check further
            pass

        # Try other common text encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                data.decode(encoding)
                # Check if content looks like text
                if self._looks_like_text(data):
                    return False
            except (UnicodeDecodeError, LookupError):
                continue

        # Analyze character distribution
        if self._looks_like_text(data):
            return False

        # When truly uncertain, prefer to treat as text
        # (better to include questionable content than exclude valid text)
        return False

    def _looks_like_text(self, data: bytes) -> bool:
        """Check if byte data looks like text based on character distribution.

        Returns True if the data appears to be text.
        """
        if not data:
            return True

        # Count printable vs non-printable characters
        printable = 0
        total = len(data)

        for byte in data:
            # Printable ASCII (32-126), common whitespace (9-13), and high-bit chars
            if (32 <= byte <= 126) or byte in (9, 10, 13) or byte >= 128:
                printable += 1

        # If more than 70% of characters are printable, consider it text
        # This threshold is intentionally low to prefer false negatives
        return (printable / total) >= 0.70
