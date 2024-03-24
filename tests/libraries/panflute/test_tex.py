import panflute as pf
import pytest
from panflute import Para, RawInline, Space, Str


@pytest.mark.parametrize("x", ["abc", "[@ref]"])
@pytest.mark.parametrize("sep", ["", "{}"])
def test_tex(x, sep):
    text = f"\\noindent{sep} {x}"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    raw = para.content[0]
    assert isinstance(raw, RawInline)
    if x == "abc":
        if sep:
            assert raw.text == f"\\noindent{sep}"
        else:
            assert raw.text == "\\noindent "
        s = para.content[1]
        if sep:
            assert isinstance(s, Space)
        else:
            assert isinstance(s, Str)
            assert s.text == "abc"
    elif sep:
        assert raw.text == f"\\noindent{sep}"
        s = para.content[1]
        assert isinstance(s, Space)
    else:
        assert raw.text == text
