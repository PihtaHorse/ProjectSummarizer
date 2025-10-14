import os
from projectsummarizer.core.analysis import compute_extension_stats, classify_extensions


def test_compute_extension_stats():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_project"))
    stats = compute_extension_stats(root, ["src/main.py", "README.md"]) 
    assert stats["py"]["count"] >= 1
    assert stats["md"]["count"] >= 1


def test_classify_extensions():
    all_stats = {"py": {"count": 2, "size": 10}, "png": {"count": 1, "size": 100}}
    effective_stats = {"py": {"count": 2, "size": 10}}
    effective, removed = classify_extensions(all_stats, effective_stats)
    assert "py" in effective and "png" in removed


