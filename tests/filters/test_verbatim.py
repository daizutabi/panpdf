import panflute as pf
from panflute import Doc

# from panpdf.filters.outputcell import OutputCell


# def test_outputcell_fenced_code():
#     text = "```julia\na = 1\n```\n\n```output\n1\n```\n"
#     code = pf.convert_text(text)[1]  # type:ignore
#     code = OutputCell().action(code, None)  # type:ignore
#     tex = pf.convert_text(code, input_format="panflute", output_format="latex")
#     assert "\\vspace{-0.5\\baselineskip}\\definecolor" in tex  # type:ignore
#     assert "\\definecolor{shadecolor}{RGB}{240,240,250}" in tex  # type:ignore
def test_create_header():
    from panpdf.filters.verbatim import create_header

    path = create_header()
    assert path.exists()
    path.read_text("utf-8").startswith("\\ifdefined\\Shaded")


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
