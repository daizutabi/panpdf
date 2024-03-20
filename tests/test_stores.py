from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_get_notebook(store: Store, fmt: str):
    nb = store.get_notebook(f"{fmt}.ipynb")
    assert isinstance(nb, dict)


def test_get_cell(store: Store, fmt: str):
    cell = store.get_cell(f"{fmt}.ipynb", f"fig:{fmt}")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_get_source(store: Store, fmt: str):
    source = store.get_source(f"{fmt}.ipynb", f"fig:{fmt}")
    assert isinstance(source, str)
    assert source.rstrip() == "import matplotlib.pyplot as plt\n\nplt.plot([-1, 1], [-1, 1])"


def test_get_outputs(store: Store, fmt: str):
    outputs = store.get_outputs(f"{fmt}.ipynb", f"fig:{fmt}")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_get_data(store: Store, fmt: str):
    data = store.get_data(f"{fmt}.ipynb", f"fig:{fmt}")
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


def test_add_data(store: Store):
    from panpdf.stores import get_data_by_type

    url = "pgf.ipynb"
    identifier = "fig:pgf"
    mime = "mime"
    data = "data"

    assert mime not in store.get_data(url, identifier)

    store.add_data(url, identifier, mime, data)

    assert mime in store.get_data(url, identifier)
    store.save_notebook(url)

    assert mime in store.get_data(url, identifier)

    outputs = store.get_outputs(url, identifier)
    output = get_data_by_type(outputs, "display_data")
    assert output
    del output[mime]

    store.save_notebook(url)

    assert mime not in store.get_data(url, identifier)
