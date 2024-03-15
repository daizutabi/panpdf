import pytest

import panpdf.jupyter.nbformat as N  # noqa: N812
from panpdf.jupyter.nbformat import Store


def test_set_id(nb):
    N.set_id(nb)
    assert nb["cells"][1]["metadata"]["id"] == "sec:import"


def test_get_ids(nb):
    ids = N.get_ids(nb)
    assert ids[0] == "fig:base64"
    assert ids[1] == "sec:import"
    assert ids[2] == "fig:matplotlib"
    assert ids[3] == "tbl:pandas"
    assert ids[-1] == "update"
    ids = N.get_ids(nb, "fig")
    assert ids[0] == "fig:base64"
    assert ids[1] == "fig:matplotlib"


def test_get_cell(nb):
    cell = N.get_cell(nb, "sec:import")
    assert cell["metadata"]["id"] == "sec:import"


def test_get_source(nb):
    source = N.get_source(nb, "fig:base64")
    out = "import matplotlib.pyplot as plt\nplt.plot([1, 3])"
    assert source == out


def test_get_outputs(nb):
    outputs = N.get_outputs(nb, "sec:import")
    output = outputs[0]
    assert output["output_type"] == "stream"
    assert output["name"] == "stdout"
    assert output["text"] == "test notebook\n"


def test_store(store: Store):
    cell = store.get_cell("sec:import", "tests/test.ipynb")
    assert cell
    assert cell["source"].startswith("# #sec:import")
    store.insert_path(0, "tests")
    cell = store.get_cell("sec:import")
    assert cell
    assert cell["source"].startswith("# #sec:import")
    assert len(store.notebooks) == 2


def test_store_reload(store: Store):
    path = "tests/test.ipynb"
    outputs = store.get_outputs("update", path)
    assert outputs
    # text1 = outputs[0]["data"]["text/plain"]
    nb = store.get_notebook()
    assert isinstance(nb, dict)
    # client = NotebookClient(nb)  # type: ignore
    # client.execute()
    # nbformat.write(nb, root / path)
    # outputs = store.get_outputs("update")
    # assert outputs
    # text2 = outputs[0]["data"]["text/plain"]
    # assert text1 != text2


def test_unknown_id(store: Store):
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_notebook("tests/invalid.ipynb")
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_cell("ZZZ", "tests/test.ipynb")
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_cell("ZZZ", "tests/invalid.ipynb")
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_outputs("ZZZ", "tests/test.ipynb")
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_outputs("ZZZ", "tests/invalid.ipynb")


def test_error():
    store = Store()
    with pytest.raises(ValueError):  # noqa: PT011
        store.get_cell("id")


def test_get_display_data_matplotlib(store: Store):
    outputs = store.get_outputs("fig:matplotlib", "tests/test.ipynb")
    assert outputs
    data = N.get_display_data(outputs)
    assert data
    assert len(data) == 2
    assert "image/png" in data
    assert "text/plain" in data


def test_get_display_data_tikz(store: Store):
    outputs = store.get_outputs("fig:tikz")
    assert outputs
    data = N.get_display_data(outputs)
    assert data
    assert len(data) == 2
    assert "image/png" in data
    assert "text/plain" in data


def test_get_execute_result_pandas(store: Store):
    outputs = store.get_outputs("tbl:pandas")
    assert outputs
    data = N.get_execute_result(outputs)
    assert data
    assert len(data) == 2
    assert "text/html" in data
    assert "text/plain" in data


def test_get_execute_result_sympy(store: Store):
    outputs = store.get_outputs("eq:sympy")
    assert outputs
    data = N.get_execute_result(outputs)
    assert data
    assert len(data) == 2
    assert "text/latex" in data
    assert "text/plain" in data


def test_get_data_by_id(store: Store):
    id_ = "eq:sympy"
    outputs = store.get_outputs("eq:sympy")
    assert outputs
    data = N.get_data_by_id(outputs, id_)
    assert data
    assert len(data) == 2
    assert "text/latex" in data
    assert "text/plain" in data

    id_ = "fig:tikz"
    outputs = store.get_outputs(id_)
    assert outputs
    data = N.get_display_data(outputs)
    assert data
    assert len(data) == 2
    assert "image/png" in data
    assert "text/plain" in data


def test_get_data(store: Store):
    id_ = "tbl:pandas"
    data = store.get_data(id_)
    assert data
    assert len(data) == 2
    assert "text/html" in data
    assert "text/plain" in data

    id_ = "fig:matplotlib"
    data = store.get_data(id_)
    assert data
    assert len(data) == 2
    assert "image/png" in data
    assert "text/plain" in data


def test_get_language(store: Store):
    assert store.get_language() == "python"
