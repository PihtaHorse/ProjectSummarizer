import magic


class BinaryLibmagicDetector:
    """Content-based binary detector using libmagic.

    Relies on libmagic for accurate binary detection.
    """

    def __init__(self) -> None:
        self._magic_mime = magic.Magic(mime=True)
        self._magic_enc = magic.Magic(mime_encoding=True)

    def is_binary(self, path: str, sample_bytes: int = 65536) -> bool:
        """Return True if the file at `path` should be treated as binary."""
        try:
            with open(path, "rb", buffering=0) as f:
                head = f.read(sample_bytes)
        except Exception:
            return True

        return self._is_binary_data(head)

    def _is_binary_data(self, data: bytes) -> bool:
        """Check if data should be treated as binary using libmagic."""
        if not data:
            return False

        try:
            # Check encoding first
            enc = self._magic_enc.from_buffer(data)
            if enc and enc != "binary":
                return False

            # Check MIME type
            mime = self._magic_mime.from_buffer(data) or ""
            low = mime.lower()

            # Text types are not binary
            if (
                low.startswith("text/")
                or ("json" in low)
                or ("+json" in low)
                or ("xml" in low)
                or ("+xml" in low)
                or low == "application/x-empty"
            ):
                return False

            return True

        except Exception:
            return True
