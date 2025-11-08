"""Binary file detection engines and factory."""

# Try to import python-magic to check availability
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from projectsummarizer.files.discovery.binary_detectors.binary_detector_protocol import BinaryDetectorProtocol
from projectsummarizer.files.discovery.binary_detectors.binary_detector_factory import BinaryDetectorFactory
from projectsummarizer.files.discovery.binary_detectors.heuristic_binary_detector import HeuristicBinaryDetector

# Only import and export BinaryLibmagicDetector if magic is available
if HAS_MAGIC:
    from projectsummarizer.files.discovery.binary_detectors.binary_libmagic_detector import BinaryLibmagicDetector
    __all__ = [
        "BinaryDetectorProtocol",
        "BinaryDetectorFactory",
        "BinaryLibmagicDetector",
        "HeuristicBinaryDetector",
    ]
else:
    __all__ = [
        "BinaryDetectorProtocol",
        "BinaryDetectorFactory",
        "HeuristicBinaryDetector",
    ]
