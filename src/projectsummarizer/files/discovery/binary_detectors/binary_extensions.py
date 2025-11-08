"""Common binary file extensions for fallback binary detection.

This blacklist is used when libmagic is not available to identify
known binary file formats by their extensions.
"""

BINARY_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.tiff', '.tif', '.webp', '.svg',
    '.psd', '.ai', '.raw', '.cr2', '.nef', '.orf', '.sr2',

    # Videos
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg',

    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus',

    # Archives
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.jar', '.war', '.ear',

    # Executables and libraries
    '.exe', '.dll', '.so', '.dylib', '.bin', '.o', '.a', '.lib', '.pyc', '.pyo', '.pyd',

    # Documents (binary formats)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',

    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot',

    # Database files
    '.db', '.sqlite', '.sqlite3', '.mdb',

    # Other binary formats
    '.class', '.dex', '.apk', '.ipa', '.dmg', '.iso', '.img',
    '.pickle', '.pkl', '.npy', '.npz', '.h5', '.hdf5',
    '.parquet', '.avro', '.orc',
    '.wasm', '.bc',
}
