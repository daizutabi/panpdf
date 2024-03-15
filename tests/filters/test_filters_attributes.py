import panflute as pf
import pytest
from panflute import (
    Caption,
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

from panpdf.filters.attributes import Attributes


def test_attributes_math_displaymath():
    text = "$$a = 1$$ {#id .cls1 k1=v1}\n$$b=1$$ {#id2 .cls2}"
    doc = Attributes().run(text)
    para = doc.content[0]  # type:ignore
    assert isinstance(para, Para)
    span = para.content[0]
    assert isinstance(span, Span)
    assert span.identifier == "id"
    assert span.classes == ["cls1"]
    assert span.attributes["k1"] == "v1"
    assert isinstance(span.content[0], Math)
    span = para.content[2]
    assert isinstance(span, Span)
    assert span.identifier == "id2"
    assert span.classes == ["cls2"]
    assert span.attributes == {}


def test_attributes_math_inlinemath():
    text = "$a = 1$ {#id .cls1 k1=v1}\n$b=1$ {#id2 .cls2}"
    doc = Attributes().run(text)
    para = doc.content[0]  # type:ignore
    assert isinstance(para, Para)
    c = para.content
    assert c[0] == Math("a = 1", format="InlineMath")
    assert c[2] == Str("{#id")
    assert c[4] == Str(".cls1")
    assert c[6] == Str("k1=v1}")


TABLE = "|   |   |\n|:-:|:-:|\n|   |   |"
CAPTION = ": caption $y=f(x)$ {#id .cls k1=v1} [@fig:1]."


@pytest.mark.parametrize(("a", "b"), [(TABLE, CAPTION), (CAPTION, TABLE)])
def test_attributes_table(a, b):
    text = f"{a}\n\n{b}"
    table = Attributes().run(text).content[0]  # type:ignore
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


def test_attributes_para_figure():
    text = "![caption $\\sqrt{2}$](a.png){#fig:id width=10cm}"
    para = Attributes().run(text).content[0]  # type:ignore
    assert isinstance(para, Para)
    assert len(para.content) == 1
    assert isinstance(para.content[0], Image)


def test_attributes_para_minifigure():
    text = "![caption a](a.png){#fig:a}\n![caption b](b.png){#fig:b}"
    para = Attributes().run(text).content[0]  # type:ignore
    assert isinstance(para, Para)
    assert len(para.content) == 3
    assert isinstance(para.content[0], Image)
    assert isinstance(para.content[1], SoftBreak)
    assert isinstance(para.content[2], Image)


def test_attributes_para_subfigure():
    text = "![a](a.png){#fig:a}\n![b](b.png){#fig:b}\n: caption\na-b"
    para = Attributes().run(text).content[0]  # type:ignore
    assert isinstance(para, Para)
    assert len(para.content) == 9
    assert isinstance(para.content[0], Image)
    assert para.content[1] == SoftBreak()
    assert isinstance(para.content[2], Image)
    assert para.content[3] == SoftBreak()
    assert para.content[4] == Str(":")
    assert para.content[5] == Space()
    assert para.content[6] == Str("caption")
    assert para.content[7] == SoftBreak()
    assert para.content[8] == Str("a-b")
