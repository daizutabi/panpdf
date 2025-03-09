import panflute as pf
import pytest
from panflute import (
    Caption,
    Cite,
    Code,
    Figure,
    Image,
    Math,
    Para,
    Plain,
    SoftBreak,
    Space,
    Span,
    Str,
    Table,
)

from panpdf.filters.attribute import Attribute


def _get_para(text: str) -> Para:
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    return para


def test_iter_attributes():
    from panpdf.filters.attribute import iter_attributes

    para = _get_para("abc {#id .cls} def")
    assert isinstance(para, Para)
    ans = [
        (Str("abc"), False),
        (Space(), False),
        (Str("{#id"), True),
        (Space(), True),
        (Str(".cls}"), True),
        (Space(), False),
        (Str("def"), False),
    ]
    for i, ei in enumerate(iter_attributes(para.content)):
        assert ei == ans[i]


def test_iter_attributes_newline():
    from panpdf.filters.attribute import iter_attributes

    para = _get_para("abc\n{#id .cls}\ndef")
    ans = [
        (Str("abc"), False),
        (SoftBreak(), False),
        (Str("{#id"), True),
        (Space(), True),
        (Str(".cls}"), True),
        (SoftBreak(), False),
        (Str("def"), False),
    ]
    for i, ei in enumerate(iter_attributes(para.content)):
        assert ei == ans[i]


def test_strip_elements():
    from panpdf.filters.attribute import strip_elements

    content = [Space(), Space(), Str("a"), Space(), Space(), Str("b")]
    x = list(strip_elements(content))
    assert x == [Str("a"), Space(), Str("b")]

    content = [Str("a"), Space(), Str("b"), Str("c"), Space(), Space()]
    x = list(strip_elements(content))
    assert x == [Str("a"), Space(), Str("b"), Str("c")]

    content = [Str("a"), Space(), SoftBreak(), Str("b"), SoftBreak()]
    x = list(strip_elements(content))
    assert x == [Str("a"), Space(), Str("b")]

    content = [SoftBreak(), Space(), Str("a"), SoftBreak(), Str("b")]
    x = list(strip_elements(content))
    assert x == [Str("a"), SoftBreak(), Str("b")]

    content = [SoftBreak(), Str("a"), SoftBreak(), Str("b"), Str("c")]
    x = list(strip_elements(content))
    assert x == [Str("a"), SoftBreak(), Str("b"), Str("c")]


def test_split_attribute():
    from panpdf.filters.attribute import split_attribute

    para = _get_para("abc $x$ {#id .cls} [@fig:1] def")
    elems, a = split_attribute(para.content)
    assert elems[0] == Str("abc")
    assert elems[1] == Space()
    assert elems[2] == pf.Math("x", format="InlineMath")
    assert elems[3] == Space()
    assert isinstance(elems[4], Cite)
    assert a == "{#id .cls}"


def test_set_attributes():
    from panpdf.filters.attribute import set_attributes

    code = Code("text")
    para = _get_para(" abc\n{#id .cls1\n.cls2 k1=v1 k2=v2} \n def ")
    rest = set_attributes(code, para.content)

    assert code.identifier == "id"
    assert code.classes == ["cls1", "cls2"]
    assert code.attributes["k1"] == "v1"
    assert code.attributes["k2"] == "v2"

    assert rest == [Str("abc"), SoftBreak(), Str("def")]

    assert set_attributes(code, para.content) is None

    assert set_attributes(Code(""), []) == []


def test_set_attributes_table():
    from panpdf.filters.attribute import set_attributes_table

    text = "|   |   |\n|:-:|:-:|\n|   |   |\n\n"
    text += ": caption $y=f(x)$ {#id .cls k1=v1} [@fig:1].\n"
    table = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(table, Table)
    set_attributes_table(table)
    assert table.identifier == "id"
    assert table.classes == ["cls"]
    assert table.attributes["k1"] == "v1"

    plain = table.caption.content[0]
    assert isinstance(plain, Plain)
    assert plain.content[0] == Str("caption")
    assert plain.content[2] == Math("y=f(x)", format="InlineMath")
    assert isinstance(plain.content[4], Cite)


TABLE = "|   |   |\n|:-:|:-:|\n|   |   |"
CAPTION = ": caption $y=f(x)$ {#id .cls k1=v1} [@fig:1]."


@pytest.mark.parametrize(("a", "b"), [(TABLE, CAPTION), (CAPTION, TABLE)])
def test_table(a, b):
    text = f"{a}\n\n{b}"
    table = Attribute().run(text).content[0]  # type:ignore
    assert isinstance(table, Table)
    assert table.identifier == "id"
    assert table.classes == ["cls"]
    assert table.attributes["k1"] == "v1"
    caption = table.caption
    assert isinstance(caption, Caption)
    plain = caption.content[0]
    assert isinstance(plain, Plain)
    assert plain.content[0] == Str("caption")
    assert isinstance(plain.content[2], Math)
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\(y=f(x)\\)" in tex


def test_set_attributes_figure():
    from panpdf.filters.attribute import set_attributes_figure

    text = "![caption $\\sqrt{2}$](a.png){#fig:id .c .d width=10cm}"
    fig = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(fig, Figure)
    set_attributes_figure(fig)

    assert fig.identifier == "fig:id"
    img = fig.content[0].content[0]  # type:ignore
    assert isinstance(img, Image)
    assert img.identifier == "fig:id"


def test_set_attributes_math():
    from panpdf.filters.attribute import set_attributes_math

    para = _get_para("$$a = 1$$ {#id .cls1 k1=v1}\n$$b=1$$ {#id2 .cls2}")
    para = set_attributes_math(para)

    span = para.content[0]
    assert isinstance(span, Span)
    assert span.identifier == "id"
    assert span.classes == ["cls1"]
    assert span.attributes["k1"] == "v1"
    assert isinstance(span.content[0], Math)

    assert isinstance(para.content[1], SoftBreak)

    span = para.content[2]
    assert isinstance(span, Span)
    assert span.identifier == "id2"
    assert span.classes == ["cls2"]
    assert span.attributes == {}
    assert isinstance(span.content[0], Math)


def test_set_attributes_image():
    from panpdf.filters.attribute import set_attributes_image

    para = _get_para("![caption a](a.png){#fig:a}\n![caption b](b.png){#fig:b}")
    fig = set_attributes_image(para)
    assert fig.caption == Caption()
    assert fig.identifier == ""
    assert fig.classes == []
    assert fig.attributes == {}


def test_set_attributes_image_caption():
    from panpdf.filters.attribute import set_attributes_image

    para = _get_para("![a](a.png){#fig:a}\n![b](b.png){#fig:b}\n: caption\na b")
    fig = set_attributes_image(para)
    assert isinstance(fig.caption, Caption)
    assert fig.identifier == ""
    assert fig.classes == []
    assert fig.attributes == {}


def test_set_attributes_image_caption_attr():
    from panpdf.filters.attribute import set_attributes_image

    para = _get_para(
        "![a](a.png){#fig:a}\n![b](b.png){#fig:b}\n: caption\na {#fig:ab .c k=v} b",
    )
    fig = set_attributes_image(para)
    assert isinstance(fig.caption, Caption)
    assert fig.identifier == "fig:ab"
    assert fig.classes == ["c"]
    assert fig.attributes == {"k": "v"}


def test_set_attributes_image_attr():
    from panpdf.filters.attribute import set_attributes_image

    para = _get_para("![a](a.png){#fig:a}\n![b](b.png){#fig:b}\n{#fig:ab .c .d}")
    fig = set_attributes_image(para)
    assert fig.caption == Caption()
    assert fig.identifier == "fig:ab"
    assert fig.classes == ["c", "d"]
    assert fig.attributes == {}


def _prepare(text: str):
    return Attribute().run(text).content[0]  # type:ignore


def test_convert_table():
    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = _prepare(text)
    assert isinstance(table, Table)
    Attribute().action(table, None)
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\caption{caption}\\label{tbl:id}" in tex
    assert tex.count("\\label{tbl:id}") == 1


def test_convert_table_without_caption():
    text = "|a|a|\n|-|-|\n|1|2|\n\n"
    table = _prepare(text)
    assert isinstance(table, Table)
    Attribute().action(table, None)
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\caption" not in tex
