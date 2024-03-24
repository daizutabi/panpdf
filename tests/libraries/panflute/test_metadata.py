import inspect

import panflute as pf
from panflute import Doc


def test_metadata():
    from panpdf.tools import get_metadata

    text = """
    ---
    x: \\includegraphics[width=2cm]{a.png}
    ---
    """
    text = inspect.cleandoc(text)
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    x = get_metadata(doc, "x")
    assert x == "\\includegraphics[width=2cm]{a.png}"
    x = get_metadata(doc, "y")
    assert x is None
