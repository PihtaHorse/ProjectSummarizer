import os
from projectsummarizer.core.ignore import collect_file_paths, parse_ignore_files


def test_collect_file_paths_respects_patterns():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_project"))
    files_no_pattern = collect_file_paths(root, [], include_ignore_files=False)
    assert any(p.endswith("assets/blob.bin") for p in files_no_pattern)

    files_ignore_bin = collect_file_paths(root, ["*.bin"], include_ignore_files=False)
    assert not any(p.endswith("assets/blob.bin") for p in files_ignore_bin)
    # sanity: still has python file
    assert any(p.endswith("src/main.py") for p in files_ignore_bin)


def test_parse_ignore_files_reads_gitignore():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_project"))
    patterns = parse_ignore_files(root)
    assert "*.bin" in patterns


