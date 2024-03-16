import panflute as pf
from panflute import Caption, Figure, Image, Para, Plain, RawInline, Space, Str


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
    tex = pf.convert_text(elems, input_format="panflute", output_format="latex")
    lines = [
        "a\n",
        "\\begin{figure}",
        "\\centering",
        "\\includegraphics{a.png}",
        "\\caption{caption \\(\\sqrt{2}\\)}\\label{fig:id}",
        "\\end{figure}",
        "\nb",
    ]
    assert tex == "\n".join(lines)


def test_figure_width():
    text = "![A](a.png){#fig:id width=1cm}"
    tex = pf.convert_text(text, output_format="latex")
    assert isinstance(tex, str)
    assert "[width=1cm,height=\\textheight]" in tex


def test_figure_multi():
    text = "a\n\n![A](a.png){#fig:a .c k=v} ![A](a.png){#fig:a .c k=v}\n\nb"
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
    assert tex == "a\n\n\\includegraphics{a.png} \\includegraphics{a.png}\n\nb"


def test_figure_class():
    image = Image(
        Str("Description"),
        title="The Title",
        url="example.png",
        attributes={"height": "256px"},
    )
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(image), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    lines = [
        "\\begin{figure}",
        "\\centering",
        "\\includegraphics[width=\\textwidth,height=2.66667in]{example.png}",
        "\\caption{The Caption}\\label{figure1}",
        "\\end{figure}",
    ]
    assert tex == "\n".join(lines)


def test_image_class():
    x = RawInline("abc\ndef", format="latex")
    y = RawInline("ghi", format="latex")
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(x, y), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    lines = [
        "\\begin{figure}",
        "\\centering",
        "abc",
        "defghi",
        "\\caption{The Caption}\\label{figure1}",
        "\\end{figure}",
    ]
    assert tex == "\n".join(lines)


def test_figure_class_multi():
    image = Image(
        Str("Description"),
        title="The Title",
        url="example.png",
        attributes={"height": "256px"},
    )
    caption = Caption(Plain(Str("The"), Space, Str("Caption")))
    figure = Figure(Plain(image, Space, image), caption=caption, identifier="figure1")
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    lines = [
        "\\begin{figure}",
        "\\centering",
        "\\includegraphics[width=\\textwidth,height=2.66667in]{example.png}",
        "\\includegraphics[width=\\textwidth,height=2.66667in]{example.png}",
        "\\caption{The Caption}\\label{figure1}",
        "\\end{figure}",
    ]
    assert tex == "\n".join(lines)


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
