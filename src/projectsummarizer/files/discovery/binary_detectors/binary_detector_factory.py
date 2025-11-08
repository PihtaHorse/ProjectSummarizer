"""Factory for creating appropriate binary detector based on libmagic availability."""

import logging

# Try to import python-magic, but make it optional
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

# Only import BinaryLibmagicDetector if magic is available
# Otherwise it will fail at import time
if HAS_MAGIC:
    from projectsummarizer.files.discovery.binary_detectors.binary_libmagic_detector import BinaryLibmagicDetector

from projectsummarizer.files.discovery.binary_detectors.heuristic_binary_detector import HeuristicBinaryDetector

logger = logging.getLogger(__name__)


class BinaryDetectorFactory:
    """Factory class that creates the appropriate binary detector.

    Returns BinaryLibmagicDetector when libmagic is available,
    otherwise returns HeuristicBinaryDetector with a warning.
    """

    _warned = False  # Class variable to ensure we only warn once

    @classmethod
    def create(cls):
        """Create and return the appropriate binary detector.

        Returns:
            BinaryLibmagicDetector if libmagic is available,
            HeuristicBinaryDetector otherwise.
        """
        if HAS_MAGIC:
            try:
                # Try to instantiate the magic detector
                detector = BinaryLibmagicDetector()
                return detector
            except Exception as e:
                if not cls._warned:
                    logger.warning(
                        "Failed to initialize libmagic: %s. "
                        "Falling back to heuristic binary detection.",
                        e
                    )
                    cls._warned = True
                return HeuristicBinaryDetector()
        else:
            if not cls._warned:
                logger.warning(
                    "libmagic not available. Using fallback heuristic binary detection. "
                    "For better accuracy and performance, install libmagic: "
                    "Ubuntu/Debian: 'sudo apt-get install libmagic1' | "
                    "macOS: 'brew install libmagic' | "
                    "Then install python-magic: 'pip install python-magic'"
                )
                cls._warned = True
            return HeuristicBinaryDetector()
