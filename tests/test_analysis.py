import os
from ps_core.analysis import compute_extension_stats, classify_extensions


def test_compute_extension_stats(tmp_path):
    root = tmp_path
    (root / "x.py").write_text("print('a')", encoding="utf-8")
    (root / "y.TXT").write_text("note", encoding="utf-8")
    stats = compute_extension_stats(str(root), ["x.py", "y.TXT"]) 
    assert stats["py"]["count"] == 1
    assert stats["txt"]["count"] == 1


def test_classify_extensions():
    all_stats = {"py": {"count": 2, "size": 10}, "png": {"count": 1, "size": 100}}
    effective_stats = {"py": {"count": 2, "size": 10}}
    effective, removed = classify_extensions(all_stats, effective_stats)
    assert "py" in effective and "png" in removed


