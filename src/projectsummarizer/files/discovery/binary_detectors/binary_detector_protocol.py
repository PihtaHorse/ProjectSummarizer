"""Protocol defining the interface for binary detectors."""

from typing import Protocol


class BinaryDetectorProtocol(Protocol):
    """Protocol defining the interface for binary detectors.

    Any class implementing this protocol must provide an is_binary method
    that determines whether a file should be treated as binary.
    """

    def is_binary(self, path: str, sample_bytes: int = 65536) -> bool:
        """Return True if the file at path should be treated as binary.

        Args:
            path: Path to the file to check
            sample_bytes: Number of bytes to read for detection (default: 65536)

        Returns:
            True if the file should be treated as binary, False otherwise
        """
        ...
