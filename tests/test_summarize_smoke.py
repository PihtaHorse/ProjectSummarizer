import os
import subprocess
import sys


def test_summarize_structure_only(tmp_path):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_project"))
    out_file = os.path.join(str(tmp_path), "summary.txt")

    cmd = [
        sys.executable,
        os.path.abspath("summarize.py"),
        "--directory",
        str(root),
        "--output_file",
        str(out_file),
        "--only_structure",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "src/main.py" in content


