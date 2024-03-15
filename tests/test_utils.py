from pathlib import Path

import panflute as pf
import pytest
from panflute import Cite, Code, Math, Para, Plain, SoftBreak, Space, Str, Table

from panpdf import utils


def test_attribute_scanner():
    text = "abc {#id .cls} def"
    para = pf.convert_text(text)[0]  # type:ignore
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
    for i, ei in enumerate(utils.attribute_scanner(para)):
        assert ei == ans[i]
    text = "abc\n{#id .cls}\ndef"
    para = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(para, Para)
    ans = [
        (Str("abc"), False),
        (SoftBreak(), False),
        (Str("{#id"), True),
        (Space(), True),
        (Str(".cls}"), True),
        (SoftBreak(), False),
        (Str("def"), False),
    ]
    for i, ei in enumerate(utils.attribute_scanner(para)):
        assert ei == ans[i]


def test_strip_content():
    content = [Space(), Space(), Str("a"), Space(), Space(), Str("b")]
    x = list(utils.strip_content(content))
    assert x == [Str("a"), Space(), Str("b")]
    content = [Str("a"), Space(), Str("b"), Str("c"), Space(), Space()]
    x = list(utils.strip_content(content))
    assert x == [Str("a"), Space(), Str("b"), Str("c")]
    content = [Str("a"), Space(), SoftBreak(), Str("b"), SoftBreak()]
    x = list(utils.strip_content(content))
    assert x == [Str("a"), Space(), Str("b")]
    content = [SoftBreak(), Space(), Str("a"), SoftBreak(), Str("b")]
    x = list(utils.strip_content(content))
    assert x == [Str("a"), SoftBreak(), Str("b")]


def test_split_attribute():
    text = "abc $x$ {#id .cls} [@fig:1] def"
    para = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(para, Para)
    c, a = utils.split_attribute(para)
    assert isinstance(c, Para)
    assert hasattr(c, "content")
    assert c.content[0] == Str("abc")
    assert c.content[2] == pf.Math("x", format="InlineMath")
    assert isinstance(c.content[4], pf.Cite)
    assert a == "{#id .cls}"
    assert pf.stringify(Plain()) == ""


def test_set_attributes():
    code = Code("text")
    text = " abc\n{#id .cls1\n.cls2 k1=v1 k2=v2} \n def "
    para = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(para, Para)
    rest = utils.set_attributes(code, para)
    assert code.identifier == "id"
    assert code.classes == ["cls1", "cls2"]
    assert code.attributes["k1"] == "v1"
    assert code.attributes["k2"] == "v2"
    assert rest == Para(Str("abc"), SoftBreak(), Str("def"))
    rest = utils.set_attributes(code, para)
    assert rest is None
    assert utils.set_attributes(Code(""), Plain()) == Plain()


def test_set_attributes_table():
    text = "|   |   |\n|:-:|:-:|\n|   |   |\n\n"
    text += ": caption $y=f(x)$ {#id .cls k1=v1} [@fig:1].\n"
    table = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(table, Table)
    plain = table.caption.content[0]  # type:ignore
    assert isinstance(plain, Plain)
    plain = utils.set_attributes(table, plain)
    assert isinstance(plain, Plain)
    assert table.identifier == "id"
    assert table.classes == ["cls"]
    assert table.attributes["k1"] == "v1"
    assert plain.content[0] == Str("caption")
    assert plain.content[2] == Math("y=f(x)", format="InlineMath")
    assert isinstance(plain.content[4], Cite)


def test_join_files(tmpdir):
    directory = Path(tmpdir)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("# a\n\n1\n")
    b.write_text("# b\n\n2\n")
    text = utils.join_files([a, b])
    assert text == "# a\n\n1\n\n\n# b\n\n2\n"


def test_collect():
    path = Path(utils.__file__).parent.parent
    paths = list(utils.collect(Path(utils.__file__), ".py"))
    assert len(paths) == 1
    paths = list(utils.collect([path], ".py"))
    assert len(paths) > 10


@pytest.mark.parametrize(
    ("path", "format"),
    [
        ("a.tex", "latex"),
        ("a.pdf", "pdf"),
    ],
)
def test_get_format(path, format):  # noqa: A002
    assert utils.get_format(path) == format


def test_get_format_unknown():
    with pytest.raises(ValueError):  # noqa: PT011
        utils.get_format("")
