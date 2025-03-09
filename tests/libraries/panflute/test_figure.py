import inspect

import panflute as pf
import pytest
from panflute import Caption, Div, Figure, Image, Para, Plain, RawInline, Space, Str


def test_figure_single():
    text = "a\n\n![caption $\\sqrt{2}$](a.png){#fig:id .c k=v}\n\nb"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    assert isinstance(elems[0], Para)
    assert isinstance(elems[2], Para)
    fig = elems[1]
    assert isinstance(fig, Figure)
    assert isinstance(fig.caption, Caption)
    assert fig.identifier == "fig:id"
    assert not fig.classes
    assert not fig.attributes
    assert not fig.container
    p = fig.content[0]
    assert isinstance(p, Plain)
    img = p.content[0]
    assert isinstance(img, Image)
    assert img.url == "a.png"
    assert not img.identifier
    assert img.classes == ["c"]
    assert img.attributes == {"k": "v"}


def test_figure_width():
    text = "![A](a.png){#fig:id width=1cm height=1cm}"
    tex = pf.convert_text(text, output_format="latex")
    assert isinstance(tex, str)
    assert "[width=1cm,height=1cm]" in tex


def test_figure_multi():
    text = (
        "a\n\n![A](a.png){#fig:a .c k=v width=1in height=1in} "
        "![A](a.png){#fig:a .c k=v width=1in height=1in}\n\nb"
    )
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    for e in elems:
        assert isinstance(e, Para)
    assert isinstance(elems[1].content[0], Image)
    img = elems[1].content[2]
    assert isinstance(img, Image)
    assert img.url == "a.png"
    assert img.identifier == "fig:a"
    assert img.classes == ["c"]
    tex = pf.convert_text(elems, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "a\n\n\\includegraphics[width=1in,height=1in]{a.png}" in tex
    assert "\\includegraphics[width=1in,height=1in]{a.png}\n\nb" in tex


def test_figure_class():
    image = Image(
        Str("Description"),
        title="The Title",
        url="example.png",
        attributes={"width": "128px", "height": "256px"},
    )
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(image), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\includegraphics[width=1.33333in,height=2.66667in]{example.png}" in tex


def test_image_class():
    x = RawInline("abc\ndef", format="latex")
    y = RawInline("ghi", format="latex")
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(x, y), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    lines = ["abc", "defghi"]
    for x in lines:
        assert x in tex


def test_figure_class_multi():
    image = Image(
        Str("Description"),
        title="The Title",
        url="example.png",
        attributes={"width": "128px", "height": "256px"},
    )
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(image, Space, image), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    lines = [
        "\\begin{figure}",
        "\\centering",
        "\\includegraphics[width=1.33333in,height=2.66667in]{example.png}",
        "\\includegraphics[width=1.33333in,height=2.66667in]{example.png}",
        "\\end{figure}",
    ]
    for x in lines:
        assert x in tex


def test_image_caption_cite():
    text = "![caption [@fig:b].](a.png){#fig:a}"
    elems = pf.convert_text(text)
    image = elems[0].content[0].content[0]  # type:ignore
    assert isinstance(image, Image)
    cite = image.content[2]
    assert isinstance(cite, pf.Cite)
    assert cite.citations[0].id == "fig:b"  # type:ignore


def test_image_caption_math():
    text = "![caption $x$.](a.png){#fig:a}"
    elems = pf.convert_text(text)
    image = elems[0].content[0].content[0]  # type:ignore
    assert isinstance(image, pf.Image)
    math = image.content[2]
    assert isinstance(math, pf.Math)
    assert math.text == "x"
    assert math.format == "InlineMath"


def test_figure_from_latex_minipage():
    tex = """
    \\begin{figure}
    \\begin{minipage}
    \\includegraphics[width=1cm]{a.png}
    \\caption{a}\\label{a}
    \\end{minipage}
    \\begin{minipage}
    \\includegraphics[width=1cm]{b.png}
    \\caption{b}\\label{b}
    \\end{minipage}
    \\end{figure}
    """
    tex = inspect.cleandoc(tex)
    x = pf.convert_text(tex, input_format="latex", output_format="latex")
    assert isinstance(x, str)
    assert "\\begin{minipage}[t]{0.45\\linewidth}" in x
    assert "\\label{a}" not in x
    assert "\\end{minipage}\n\\caption{b}\\label{b}" in x
    assert x.count("\\label{b}") == 1
    x = pf.convert_text(tex, input_format="latex", output_format="panflute")
    assert isinstance(x, list)
    assert len(x) == 1
    fig = x[0]
    assert isinstance(fig, Figure)
    assert fig.identifier == "b"
    assert len(fig.content) == 2
    for x in fig.content:
        if isinstance(x, Plain):  # pandoc <= v3.5
            assert len(x.content) == 1
            assert isinstance(x.content[0], Image)
        elif isinstance(x, Div):  # pandoc v3.6
            assert len(x.content) == 1
            assert isinstance(x.content[0], Plain)
            y = x.content[0]
            assert isinstance(y, Plain)
            assert len(y.content) == 1
            assert isinstance(y.content[0], Image)
        else:
            pytest.fail(f"Unexpected element: {type(x)}")


def test_figure_from_panflute_subfigure():
    ia = Plain(
        Image(Str("A"), url="a.png", attributes={"width": "1cm", "height": "2cm"}),
    )
    a = Figure(ia, caption=Caption(Plain(Str("a"))), identifier="a")
    ib = Plain(
        Image(Str("B"), url="b.png", attributes={"width": "3cm", "height": "4cm"}),
    )
    b = Figure(ib, caption=Caption(Plain(Str("b"))), identifier="b")
    f = Figure(a, b, caption=Caption(Plain(Str("c"))), identifier="c")
    x = pf.convert_text(f, input_format="panflute", output_format="latex")
    assert isinstance(x, str)
    assert "\\includegraphics[width=3cm,height=4cm]{b.png}\n\\caption{b}\\label{b}" in x
    assert "\\end{subfigure}\n\\caption{c}\\label{c}" in x
    assert x.count("\\label{b}") == 1
    assert x.count("\\label{c}") == 1


def test_figure_from_panflute_subfigure_none():
    ia = Plain(
        Image(Str("A"), url="a.png", attributes={"width": "1cm", "height": "2cm"}),
    )
    a = Figure(ia, caption=Caption(Plain(Str("a"))), identifier="a")
    ib = Plain(
        Image(Str("B"), url="b.png", attributes={"width": "3cm", "height": "4cm"}),
    )
    b = Figure(ib, caption=Caption(Plain(Str("b"))), identifier="b")
    f = Figure(a, b, identifier="c")
    x = pf.convert_text(f, input_format="panflute", output_format="latex")
    assert isinstance(x, str)
    assert "\\includegraphics[width=3cm,height=4cm]{b.png}\n\\caption{b}\\label{b}" in x
    assert "\\end{subfigure}\n\\caption{}\\label{c}" in x
    assert x.count("\\label{b}") == 1
    assert x.count("\\label{c}") == 1
