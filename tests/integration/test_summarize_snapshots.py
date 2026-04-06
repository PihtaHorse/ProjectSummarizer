"""Integration tests: run summarize.py main() on test_project and compare against golden snapshots.

To regenerate snapshots after an intentional output change:
    poetry run pytest tests/integration/ --update-snapshots
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# scripts/ is not a package, so load summarize.py directly by file path
_summarize_spec = importlib.util.spec_from_file_location(
    "summarize",
    Path(__file__).parent.parent.parent / "scripts" / "summarize.py",
)
_summarize_module = importlib.util.module_from_spec(_summarize_spec)
_summarize_spec.loader.exec_module(_summarize_module)
main = _summarize_module.main

SNAPSHOTS_DIR = Path(__file__).parent.parent / "resources" / "snapshots"
TEST_PROJECT_DIR = Path(__file__).parent.parent / "resources" / "test_project"


@pytest.mark.parametrize("fmt,snapshot_file", [
    ("text",     "test_project.text"),
    ("xml",      "test_project.xml"),
    ("markdown", "test_project.markdown"),
])
def test_summarize_output_matches_snapshot(fmt, snapshot_file, tmp_path, update_snapshots):
    output_file = tmp_path / f"output.{fmt}"

    argv = [
        "summarize.py",
        "--directory", str(TEST_PROJECT_DIR),
        "--no_defaults",
        "--no_gitignore",
        "--format", fmt,
        "--output_file", str(output_file),
    ]

    with patch.object(sys, "argv", argv):
        main()

    actual = output_file.read_text(encoding="utf-8")
    snapshot_path = SNAPSHOTS_DIR / snapshot_file

    if update_snapshots:
        snapshot_path.write_text(actual, encoding="utf-8")
        pytest.skip(f"Snapshot updated: {snapshot_path}")

    expected = snapshot_path.read_text(encoding="utf-8")
    assert actual == expected, (
        f"Output for --format {fmt} does not match snapshot {snapshot_file}.\n"
        f"Run with --update-snapshots to regenerate."
    )
