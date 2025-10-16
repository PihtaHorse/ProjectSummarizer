"""
Shared constants for ignore patterns across all CLI scripts.
"""

# Default patterns that should always be ignored
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    ".env",
    ".env.local",
    ".env.*.local",
    "node_modules",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".coverage",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
]

# Binary file patterns for --exclude-binary flag
BINARY_IGNORE_PATTERNS = [
    # Images
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.tiff", "*.webp", "*.svg", "*.ico",
    # Videos
    "*.mp4", "*.avi", "*.mov", "*.wmv", "*.flv", "*.webm", "*.mkv", "*.m4v",
    # Audio
    "*.mp3", "*.wav", "*.flac", "*.aac", "*.ogg", "*.m4a", "*.wma",
    # Archives
    "*.zip", "*.tar", "*.gz", "*.rar", "*.7z", "*.bz2", "*.xz", "*.tar.gz", "*.tar.bz2",
    # Executables and libraries
    "*.exe", "*.dll", "*.so", "*.dylib", "*.bin", "*.obj", "*.o", "*.a", "*.lib",
    # Compiled code
    "*.pyc", "*.pyo", "*.class", "*.jar", "*.war", "*.ear",
    # Packages and installers
    "*.apk", "*.ipa", "*.deb", "*.rpm", "*.msi", "*.dmg", "*.iso", "*.app",
    # Database files
    "*.db", "*.sqlite", "*.sqlite3", "*.mdb", "*.accdb",
    # Fonts
    "*.ttf", "*.otf", "*.woff", "*.woff2", "*.eot",
]
