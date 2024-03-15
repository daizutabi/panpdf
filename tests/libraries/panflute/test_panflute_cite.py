import panflute as pf
from panflute import Citation, Cite


def test_cite():
    text = "@fig:1"
    elems = pf.convert_text(text)
    cite = elems[0].content[0]  # type:ignore
    assert isinstance(cite, Cite)
    assert cite.content[0].text == "@fig:1"  # type:ignore
    assert isinstance(cite.citations[0], Citation)
    assert cite.citations[0].id == "fig:1"  # type:ignore

    text = "[@fig:1; @fig:2]"
    elems = pf.convert_text(text)
    cite = elems[0].content[0]  # type:ignore
    assert isinstance(cite, Cite)
    assert cite.citations[0].id == "fig:1"  # type:ignore
    assert cite.citations[1].id == "fig:2"  # type:ignore
