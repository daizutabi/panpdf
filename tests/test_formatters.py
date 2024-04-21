import base64
import io
import re
from pathlib import Path

import holoviews as hv
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import pytest
import seaborn.objects as so
from holoviews.core.options import Store
from IPython.core.formatters import PlainTextFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.lib.pretty import RepresentationPrinter

mpl.use("agg")


def test_matplotlib_figure(fmt):
    from panpdf.formatters import FUNCTIONS

    if fmt == "png":
        return

    functions = FUNCTIONS.get(("matplotlib.figure", "Figure"))
    assert functions
    function = functions.get(fmt)
    assert function

    fig, ax = plt.subplots()
    ax.plot([-1, 1], [-1, 1])

    if fmt == "pgf":
        out = io.StringIO()
        rp = RepresentationPrinter(out)

        function(fig, rp, None)
        text = out.getvalue()
        assert text.startswith("%% Creator: Matplotlib, PGF backend")
        assert text.endswith("\\endgroup%\n")

    elif fmt == "pdf":
        data = function(fig)
        assert isinstance(data, bytes)
        assert base64.b64encode(data).decode().startswith("JVBER")

    elif fmt == "svg":
        xml = function(fig)
        assert isinstance(xml, str)
        assert xml.startswith('<?xml version="1.0"')


def test_seaborn_plot(fmt):
    from panpdf.formatters import FUNCTIONS

    if fmt == "png":
        return

    functions = FUNCTIONS.get(("seaborn._core.plot", "Plot"))
    assert functions
    function = functions.get(fmt)
    assert function

    p = so.Plot()

    if fmt == "pgf":
        out = io.StringIO()
        rp = RepresentationPrinter(out)

        function(p, rp, None)
        text = out.getvalue()
        assert text.startswith("%% Creator: Matplotlib, PGF backend")
        assert text.endswith("\\endgroup%\n")

    elif fmt == "pdf":
        data = function(p)
        assert isinstance(data, bytes)
        assert base64.b64encode(data).decode().startswith("JVBER")

    elif fmt == "svg":
        xml = function(p)
        assert isinstance(xml, str)
        assert xml.startswith('<?xml version="1.0"')


def test_set_formatter():
    from panpdf.formatters import matplotlib_figure_to_pgf, set_formatter

    ip = InteractiveShell()
    set_formatter("matplotlib", "pgf", ip)
    formatter = ip.display_formatter.formatters["text/plain"]  # type:ignore
    assert isinstance(formatter, PlainTextFormatter)
    func = formatter.lookup_by_type("matplotlib.figure.Figure")
    assert func is matplotlib_figure_to_pgf


def test_set_formatter_none():
    from panpdf.formatters import set_formatter

    set_formatter("matplotlib", "pgf")


@pytest.fixture(scope="module")
def curve():
    from panpdf.formatters import set_formatter

    set_formatter("holoviews", "pgf")
    hv.extension("matplotlib")  # type: ignore

    df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    return hv.Curve(df, "x", "y")


def test_set_formatter_holoviews(curve):
    renderer = Store.renderers["matplotlib"]
    plot = renderer.get_plot(curve)
    data, metadata = renderer(plot, fmt="pgf")
    assert isinstance(data, bytes)
    assert data.startswith(b"%% Creator: Matplotlib, PGF backend\n%")
    assert isinstance(metadata, dict)
    assert metadata["mime_type"] == "text/pgf"


@pytest.fixture(scope="module")
def text():
    from panpdf.formatters import matplotlib_figure_to_pgf

    data = np.random.randn(50, 50)
    fig, ax = plt.subplots(figsize=(3, 2))
    a = ax.imshow(data, interpolation="nearest", aspect=1)
    ax.set(xlabel="x", ylabel="α")
    fig.colorbar(a)

    out = io.StringIO()
    rp = RepresentationPrinter(out)

    matplotlib_figure_to_pgf(fig, rp, None)
    return out.getvalue()


def test_matplotlib_figure_to_pgf_raster(text: str):
    assert "\n%% __panpdf_begin__\n" in text
    assert text.endswith("%% __panpdf_end__")


def test_split_pgf_text(text: str):
    from panpdf.formatters import split_pgf_text

    text, image_dict = split_pgf_text(text)
    assert text.startswith("%% Creator: Matplotlib, PGF backend")
    assert text.endswith("\\endgroup%\n")

    for name, data in image_dict.items():
        assert name in text
        assert data.startswith("iVBOR")
        assert not data.endswith("\n")


def test_split_pgf_text_none():
    from panpdf.formatters import split_pgf_text

    text, image_dict = split_pgf_text("abc")
    assert text == "abc"
    assert not image_dict


def test_convert_pgf_text(text: str):
    from panpdf.formatters import convert_pgf_text

    text = convert_pgf_text(text)

    for x in re.findall(r"\\includegraphics\[.+?\]{(.+?)}", text):
        assert Path(x).exists()


def test_convert_pgf_text_none():
    from panpdf.formatters import convert_pgf_text

    assert convert_pgf_text("abc") == "abc"
