import panflute as pf
from panflute import Math, Plain, Span


def test_span():
    s = Span(Math("x=1"), identifier="x", classes=["c"], attributes={"k": "v"})
    tex = pf.convert_text(Plain(s), input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert tex == "\\phantomsection\\label{x}{\\[x=1\\]}"
