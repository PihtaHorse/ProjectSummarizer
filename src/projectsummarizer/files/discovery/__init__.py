from projectsummarizer.files.discovery.ignore import IgnorePatternsHandler
from projectsummarizer.files.discovery.discoverer import FileDiscoverer
from projectsummarizer.files.discovery.binary_detectors import (
    BinaryDetectorProtocol,
    BinaryDetectorFactory,
    HeuristicBinaryDetector,
)

# Try to import BinaryLibmagicDetector if available
try:
    from projectsummarizer.files.discovery.binary_detectors import BinaryLibmagicDetector
    HAS_LIBMAGIC_DETECTOR = True
except ImportError:
    HAS_LIBMAGIC_DETECTOR = False

# Build __all__ based on what's available
__all__ = [
    "IgnorePatternsHandler",
    "FileDiscoverer",
    "BinaryDetectorProtocol",
    "BinaryDetectorFactory",
    "HeuristicBinaryDetector",
]

if HAS_LIBMAGIC_DETECTOR:
    __all__.append("BinaryLibmagicDetector")
