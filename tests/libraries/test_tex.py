import panflute as pf
from panflute import Para, RawInline, Str


def test_tex():
    text = "\\noindent abc"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    raw = para.content[0]
    assert isinstance(raw, RawInline)
    assert raw.text == "\\noindent "
    s = para.content[1]
    assert isinstance(s, Str)
    assert s.text == "abc"
