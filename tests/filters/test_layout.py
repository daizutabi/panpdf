import panflute as pf
from panflute import Doc, Figure, Para, RawInline, Span, Table

from panpdf.filters.attribute import Attribute
from panpdf.filters.jupyter import Jupyter


def _prepare(text: str):
    return Attribute().run(text).content[0]  # type:ignore


def test_convert_span_equation():
    from panpdf.filters.layout import convert_span

    text = "$$x=1$$ {#id}"
    span = _prepare(text).content[0]  # type:ignore
    assert isinstance(span, Span)
    r = convert_span(span)
    assert isinstance(r, RawInline)
    text = "\\begin{equation}\nx=1\\label{id}\n\\end{equation}\n"
    assert r.text == text
    assert r.format == "latex"


def test_convert_span_eqnarray():
    from panpdf.filters.layout import convert_span

    text = "$$x=1\\\\\ny=2$$ {#id}"
    span = _prepare(text).content[0]  # type:ignore
    assert isinstance(span, Span)
    m = convert_span(span)
    assert isinstance(m, RawInline)
    text = "\\begin{eqnarray}\nx=1\\\\\ny=2\\label{id}\n\\end{eqnarray}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_span():
    from panpdf.filters.layout import convert_span

    span = _prepare("$$x=1$$").content[0]  # type:ignore
    assert isinstance(span, Span)
    s = convert_span(span)
    assert isinstance(s, Span)


def test_convert_table():
    from panpdf.filters.layout import convert_table

    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = _prepare(text)
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


def test_create_figure_from_image(store, defaults, fmt):
    if fmt == "svg":
        return

    from panpdf.filters.layout import create_figure_from_image, get_images

    text = f"![A]({fmt}.ipynb){{#fig:{fmt}}}"
    fig = _get_figure(text)
    images = get_images(fig)
    image = images[0]
    image = Jupyter(store=store, defaults=defaults).action(images[0], Doc())
    fig = create_figure_from_image(image)
    tex = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    if fmt == "pgf":
        assert "\\endgroup%\n\\caption{A}" in tex
    else:
        assert f".{fmt}}}\n" in tex
    assert f"\\caption{{A}}\\label{{fig:{fmt}}}" in tex


def test_convert_figure_minipage():
    from panpdf.filters.layout import convert_figure

    text = "![A $x$](a.png){#fig:a hspace=1mm}\n"
    text += "![B](b.png){#fig:b cwidth=3cm}"

    fig = _get_figure(text)
    fig = convert_figure(fig)
    tex = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\hspace{1mm}%\n\\begin{minipage}{3cm}" in tex
    assert "height" not in tex
    assert "\\caption{}" not in tex


def test_convert_figure_subfigure():
    from panpdf.filters.layout import convert_figure

    text = "![A $x$](a.png){#fig:a hspace=1mm}\n"
    text += "![B](b.png){#fig:b cwidth=3cm}\n"
    text += ": x $m$ {#fig:X}"

    fig = _get_figure(text)
    fig = convert_figure(fig)
    tex = pf.convert_text(fig, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\hspace{1mm}%\n\\begin{subfigure}{3cm}" in tex
    assert "\\caption{x \\(m\\)}\\label{fig:X}" in tex