"""Appends each summarize.py invocation to a persistent history log."""

import shlex
from datetime import datetime
from pathlib import Path

LOG_FILENAME = "history.log"


def log_call(argv: list[str], project_dir: str) -> None:
    """Append the current invocation to the history log in the project root.

    Each entry is a single line:
        [2026-04-06 14:23:01] summarize.py --directory /path --format xml ...

    Args:
        argv: sys.argv from the calling script
        project_dir: root directory of the summarized project
    """
    log_path = Path(project_dir) / LOG_FILENAME

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = shlex.join(argv)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {command}\n")
