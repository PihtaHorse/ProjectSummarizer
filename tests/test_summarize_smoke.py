import os
import subprocess
import sys


def test_summarize_structure_only(tmp_path):
    root = tmp_path
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
    out_file = root / "summary.txt"

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
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "src/main.py" in content


