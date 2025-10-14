import os
from ps_core.ignore import collect_file_paths, should_ignore, parse_ignore_files


def test_collect_file_paths_respects_patterns(tmp_path):
    root = tmp_path
    (root / "a").mkdir()
    (root / "a" / "keep.txt").write_text("hi", encoding="utf-8")
    (root / "a" / "skip.bin").write_text("xx", encoding="utf-8")

    files = collect_file_paths(str(root), ["*.bin"], include_ignore_files=False)
    assert "a/keep.txt" in files
    assert "a/skip.bin" not in files


def test_parse_ignore_files_reads_gitignore(tmp_path):
    root = tmp_path
    (root / ".gitignore").write_text("*.png\n# comment\n\n*.jpg", encoding="utf-8")
    patterns = parse_ignore_files(str(root))
    assert "*.png" in patterns and "*.jpg" in patterns


