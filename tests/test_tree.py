from ps_core.tree import build_tree_structure, print_tree


def test_build_and_print_tree():
    paths = [
        "src/main.py",
        "README.md",
    ]
    tree = build_tree_structure(paths)
    out = print_tree(tree)
    assert "src/" in out
    assert "main.py" in out
    assert "README.md" in out


