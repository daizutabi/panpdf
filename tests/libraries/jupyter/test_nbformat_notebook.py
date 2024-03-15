import nbformat


def test_notebook():
    nb = nbformat.v4.new_notebook()
    assert isinstance(nb, dict)
    assert len(nb) == 4
    assert nb["nbformat"] == 4
    assert nb["nbformat_minor"] >= 5
    assert nb["metadata"] == {}
    assert nb["cells"] == []


def test_code_cell():
    source = "a = 1\na\n"
    cell = nbformat.v4.new_code_cell(source)
    assert isinstance(cell, dict)
    assert len(cell) == 6
    assert cell["id"]
    assert cell["cell_type"] == "code"
    assert cell["metadata"] == {}
    assert cell["execution_count"] is None
    assert cell["source"] == source
    assert cell["outputs"] == []
