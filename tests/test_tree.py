from ps_core.tree import build_tree_structure, print_tree


def test_build_and_print_tree():
    paths = [
        "a/b/c.txt",
        "a/b/d.txt",
        "a/e.txt",
        "root.txt",
    ]
    tree = build_tree_structure(paths)
    out = print_tree(tree)
    assert "a/" in out
    assert "c.txt" in out and "d.txt" in out and "e.txt" in out and "root.txt" in out


