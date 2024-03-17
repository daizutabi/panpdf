import inspect

import panflute as pf
from panflute import Doc


def test_run():
    from panpdf.filters.crossref import Crossref

    text = """
    ---
    figure-ref-name: XXX
    ---
    [@sec:section] [@sec:subsection]
    [@fig:pgf] [@fig:png] [@fig:pdf]
    [@tbl:markdown]
    [@eq:markdown]
    [@abc]
    """
    doc = pf.convert_text(inspect.cleandoc(text), standalone=True)
    assert isinstance(doc, Doc)
    crossref = Crossref()
    doc = crossref.run(doc)
    tex = pf.convert_text(doc, input_format="panflute", output_format="latex")
    for ref in [
        "\\ref{sec:section}",
        "XXX~\\ref{fig:pgf}",
        "XXX~\\ref{fig:pdf}",
        "XXX~\\ref{fig:png}",
        "Table~\\ref{tbl:markdown}",
        "Eq.~\\ref{eq:markdown}",
        "{[}@abc{]}",
    ]:
        assert ref in tex  # type:ignore
