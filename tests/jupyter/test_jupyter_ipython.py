import panpdf.jupyter.nbformat as N  # noqa: N812


def test_matplotlib_figure(nb):
    outputs = N.get_outputs(nb, "fig:matplotlib")
    assert outputs
    assert len(outputs) == 2
    for output in outputs:
        if output["output_type"] == "display_data":
            data = output["data"]
            assert len(data) == 2
            assert len(data["image/png"]) > 100
            assert "%% Creator: Matplotlib, PGF" in data["text/plain"]


def test_pandas_table(nb):
    outputs = N.get_outputs(nb, "tbl:pandas")
    assert outputs
    assert len(outputs) == 1
    output = outputs[0]
    assert output["output_type"] == "execute_result"
    data = output["data"]
    assert len(data) == 2
    assert "text/plain" in data
    assert "text/html" in data


def test_sympy_equation(nb):
    outputs = N.get_outputs(nb, "eq:sympy")
    assert outputs
    assert len(outputs) == 1
    output = outputs[0]
    assert output["output_type"] == "execute_result"
    data = output["data"]
    assert len(data) == 2
    assert "text/plain" in data
    assert "text/latex" in data
    assert data["text/latex"] == "$\\displaystyle y = f{\\left(x \\right)}$"


def test_tikz_figure(nb):
    outputs = N.get_outputs(nb, "fig:tikz")
    assert outputs
    assert len(outputs) == 2
    for output in outputs:
        if output["output_type"] == "execute_result":
            data = output["data"]
            assert len(data) == 1
            assert data["text/plain"].startswith("Tikz(")
        if output["output_type"] == "display_data":
            data = output["data"]
            assert len(data) == 2
            assert len(data["image/png"]) > 100
            assert "\\begin{tikzpicture}" in data["text/plain"]
