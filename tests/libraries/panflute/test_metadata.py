import inspect

import panflute as pf
from panflute import Doc


def test_get_metadata_str():
    from panpdf.tools import get_metadata_str

    text = """
    ---
    x: \\includegraphics[width=2cm]{a.png}
    ---
    """
    text = inspect.cleandoc(text)
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    x = get_metadata_str(doc, "x")
    assert x == "\\includegraphics[width=2cm]{a.png}"
    x = get_metadata_str(doc, "y")
    assert x is None


def test_header_includes():
    doc = Doc()
    doc.metadata["header-includes"] = "AAA\nBBB"
    x = pf.convert_text(
        doc, input_format="panflute", output_format="markdown", standalone=True,
    )
    assert isinstance(x, str)
    assert "---\nheader-includes: AAA BBB\n---\n" in x

    x = pf.convert_text(
        doc, input_format="panflute", output_format="latex", standalone=True,
    )
    assert isinstance(x, str)
    assert "AAA BBB" in x


def test_multilines():
    text = """
    ---
    header-includes: |
      a
      b
      c
    ---
    """
    text = inspect.cleandoc(text)
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    assert isinstance(doc.metadata["header-includes"], pf.MetaBlocks)
