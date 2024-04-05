import panflute as pf
from panflute import Doc


def test_create_header():
    from panpdf.filters.verbatim import create_header

    path = create_header()
    assert path.exists()
    text = path.read_text("utf-8")
    assert text.startswith("\\ifdefined\\Shaded")


def test_verbatim():
    from panpdf.filters.verbatim import Verbatim

    verbatim = Verbatim()
    assert not verbatim.shaded

    text = "```python\n1\n```\n\n```python {.output}\n1\n```"
    doc = verbatim.run(text)
    assert isinstance(doc, Doc)
    assert verbatim.shaded

    t = pf.convert_text(doc, input_format="panflute", output_format="latex", standalone=True)
    assert isinstance(t, str)
    assert "\\vspace{-0.5\\baselineskip}" in t
