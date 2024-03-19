import panflute as pf
from panflute import Caption, Cite, Math, Table


def test_table():
    text = "|a|b|\n|-|-|\n\n: table caption {#id .cls1 .cls2 k1=v1 k2=100}"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    table = elems[0]
    assert isinstance(table, Table)
    caption = table.caption
    assert isinstance(caption, Caption)
    assert pf.stringify(caption) == "table caption {#id .cls1 .cls2 k1=v1 k2=100}"
    assert table.identifier == ""
    assert table.classes == []
    assert table.attributes == {}


def test_table_caption_cite():
    text = "|a|b|\n|-|-|\n\n: caption [@fig:1]."
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    table = elems[0]
    assert isinstance(table, Table)
    cite = table.caption.content[0].content[2]  # type:ignore
    assert isinstance(cite, Cite)


def test_table_caption_math():
    text = "|a|b|\n|-|-|\n\n: caption $x$."
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    table = elems[0]
    assert isinstance(table, Table)
    math = table.caption.content[0].content[2]  # type:ignore
    assert isinstance(math, Math)
