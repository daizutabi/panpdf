from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from panpdf.jupyter.stores import Store


def test_get_notebook(store: Store, fmt: str):
    nb = store.get_notebook(f"{fmt}.ipynb")
    assert isinstance(nb, dict)


def test_get_cell(store: Store, fmt: str):
    cell = store.get_cell(f"fig:{fmt}", f"{fmt}.ipynb")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_get_source(store: Store, fmt: str):
    source = store.get_source(f"fig:{fmt}", f"{fmt}.ipynb")
    assert isinstance(source, str)
    assert source.rstrip() == "import matplotlib.pyplot as plt\n\nplt.plot([-1, 0, 1])"


def test_get_outputs(store: Store, fmt: str):
    outputs = store.get_outputs(f"fig:{fmt}", f"{fmt}.ipynb")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_get_data(store: Store, fmt: str):
    data = store.get_data(f"fig:{fmt}", f"{fmt}.ipynb")
    assert isinstance(data, dict)
    assert len(data) == 3 if fmt in ["pdf", "svg"] else 2
    assert "text/plain" in data
    assert "image/png" in data
    if fmt == "pgf":
        assert data["text/plain"].startswith("%% Creator: Matplotlib,")
    if fmt == "png":
        assert data["image/png"].startswith("iVBO")
    if fmt == "pdf":
        assert data["application/pdf"].startswith("JVBE")
    if fmt == "svg":
        assert data["image/svg+xml"].startswith('<?xml version="1.0"')
