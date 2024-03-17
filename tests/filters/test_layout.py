import os
from pathlib import Path

import panflute as pf
from panflute import Doc, Figure, Math, Para, Plain, RawInline, Table

from panpdf.filters.attribute import Attribute
from panpdf.filters.jupyter import Jupyter
from panpdf.filters.layout import Layout


def _convert(text: str):
    return Attribute().run(text).content[0]  # type:ignore


def test_convert_math_equation():
    from panpdf.filters.layout import convert_math

    text = "$$x=1$$ {#id}"
    math = _convert(text).content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, RawInline)
    text = "\\begin{equation}\nx=1\\label{id}\n\\end{equation}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math_eqnarray():
    from panpdf.filters.layout import convert_math

    text = "$$x=1\\\\\ny=2$$ {#id}"
    math = _convert(text).content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, RawInline)
    text = "\\begin{eqnarray}\nx=1\\\\\ny=2\\label{id}\n\\end{eqnarray}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math():
    from panpdf.filters.layout import convert_math

    math = _convert("$$x=1$$").content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, Math)


def test_convert_table():
    from panpdf.filters.layout import convert_table

    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = _convert(text)
    assert isinstance(table, Table)
    Attribute().action(table, None)
    table = convert_table(table)
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert "\\caption{\\label{tbl:id}caption}" in tex  # type:ignore


def _get_figure(text: str) -> Figure:
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Figure | Para)
    fig = Attribute().action(para, None)
    assert isinstance(fig, Figure)
    return fig


def test_get_images():
    from panpdf.filters.layout import get_images

    text = "![A](a.png){#fig:a}![B](b.png){#fig:b}![C](c.png){#fig:c}"
    fig = _get_figure(text)
    assert len(get_images(fig)) == 3


def test_convert_image(store, fmt, tmp_path):
    if fmt == "svg":
        return

    from panpdf.filters.layout import convert_image, get_images

    os.chdir(tmp_path)
    Layout().prepare(Doc())

    text = f"![A]({fmt}.ipynb){{#fig:{fmt}}}"
    fig = _get_figure(text)
    images = get_images(fig)
    image = images[0]
    image = Jupyter(store=store).action(images[0], Doc())
    image = convert_image(image, standalone=False)
    if fmt == "pgf":
        assert image.url.startswith("%%")
    else:
        assert Path(image.url).exists()


def test_convert_image_external(store, tmp_path):
    from panpdf.filters.layout import convert_image, get_images

    os.chdir(tmp_path)
    Layout(standalone=True).prepare(Doc())

    text = "![A](pgf.ipynb){#fig:pgf}"
    fig = _get_figure(text)
    images = get_images(fig)
    image = images[0]
    image = Jupyter(store=store).action(images[0], Doc())
    image = convert_image(image, standalone=True)
    assert Path(image.url).exists()


def test_add_images():
    from panpdf.filters.layout import get_images

    text = "![A](pgf.ipynb){#fig:pgf}"
    fig = _get_figure(text)
    images = get_images(fig)
    assert len(images) == 1
    fig.content = [Plain(*images, *images)]
    images = get_images(fig)
    assert len(images) == 2


def _convert_store(text: str, store) -> Figure:
    from panpdf.filters.layout import get_images

    fig = _get_figure(text)
    jupyter = Jupyter(store=store)
    for image in get_images(fig):
        jupyter.action(image, Doc())

    return fig


def test_convert_figure_single(store, fmt, tmp_path):
    if fmt == "svg":
        return

    from panpdf.filters.layout import convert_figure

    os.chdir(tmp_path)
    Layout(standalone=True).prepare(Doc())

    text = f"![A]({fmt}.ipynb){{#fig:{fmt} width=1cm}}"
    fig = _convert_store(text, store)
    fig = convert_figure(fig, standalone=False)
    x = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(x, str)
    if fmt == "pgf":
        assert x.startswith("\\begin{figure}\n\\centering\n%% Creator")
        assert x.endswith("\\endgroup%\n\\caption{A}\\label{fig:pgf}\n\\end{figure}")
    else:
        assert x.startswith("\\begin{figure}\n\\centering\n\\includegraphics[w")
        assert f"{fmt}.{fmt}" in x
        assert x.endswith(f"\\caption{{A}}\\label{{fig:{fmt}}}\n\\end{{figure}}")


def test_convert_figure_minipage(store, fmt, tmp_path):
    if fmt == "svg":
        return

    from panpdf.filters.layout import convert_figure

    os.chdir(tmp_path)
    Layout(standalone=True).prepare(Doc())

    text = f"![A $x$]({fmt}.ipynb){{#fig:{fmt} hspace=1mm}}\n"
    text += f"![B]({fmt}.ipynb){{#fig:{fmt} cwidth=3cm}}"

    fig = _convert_store(text, store)
    fig = convert_figure(fig, standalone=False)
    x = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(x, str)
    assert "\\hspace{1mm}%\n\\begin{minipage}{3cm}" in x
    assert "height" not in x
    assert "\\caption{}" not in x


def test_convert_figure_subfigure(store, fmt, tmp_path):
    if fmt == "svg":
        return

    from panpdf.filters.layout import convert_figure

    os.chdir(tmp_path)
    Layout(standalone=True).prepare(Doc())

    text = f"![A $x$]({fmt}.ipynb){{#fig:{fmt} hspace=1mm}}\n"
    text += f"![B]({fmt}.ipynb){{#fig:{fmt} cwidth=3cm}}\n"
    text += ": x $m$ {#fig:X}"

    fig = _convert_store(text, store)
    fig = convert_figure(fig, standalone=False)
    x = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(x, str)
    assert "\\hspace{1mm}%\n\\begin{subfigure}{3cm}" in x
    assert "\\caption{x \\(m\\)}\\label{fig:X}" in x
