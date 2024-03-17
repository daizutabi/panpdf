import panflute as pf
from panflute import Header


def test_section():
    text = "# section {#id .cls1 .cls2 k1=v1 k2=100}\n\n## subsection {#id2 .cls3}\n"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    header = elems[0]
    assert isinstance(header, Header)
    assert header.level == 1
    assert pf.stringify(header) == "section"
    assert header.identifier == "id"
    assert header.classes == ["cls1", "cls2"]
    assert header.attributes["k1"] == "v1"
    assert header.attributes["k2"] == "100"
    header = elems[1]
    assert isinstance(header, Header)
    assert header.level == 2
    assert pf.stringify(header) == "subsection"
    assert header.identifier == "id2"
    assert header.classes == ["cls3"]
    assert header.attributes == {}
