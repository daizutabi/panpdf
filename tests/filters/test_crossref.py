import inspect

import panflute as pf
from panflute import Doc


def test_run():
    from panpdf.filters.crossref import Crossref

    text = """
    ---
    reference-figure-name: XXX
    ---
    [@sec:section] [@sec:subsection]
    [@fig:pgf] [@fig:png] [@fig:pdf]
    [@tbl:markdown]
    [@eq:markdown]
    X [@eq:bare_] X
    [@abc]
    """
    doc = pf.convert_text(inspect.cleandoc(text), standalone=True)
    assert isinstance(doc, Doc)
    crossref = Crossref()
    doc = crossref.run(doc)
    tex = pf.convert_text(doc, input_format="panflute", output_format="latex")
    for ref in [
        "\\ref{sec:section}",
        "\\ref{sec:subsection}",
        "XXX~\\ref{fig:pgf}",
        "XXX~\\ref{fig:pdf}",
        "XXX~\\ref{fig:png}",
        "Table~\\ref{tbl:markdown}",
        "Eq.~\\ref{eq:markdown}",
        "X \\ref{eq:bare} X",
        "{[}@abc{]}",
    ]:
        assert ref in tex  # type:ignore


def test_set_prefix():
    from panpdf.filters.crossref import Crossref

    crossref = Crossref()
    crossref.set_prefix("a", "A")
    assert crossref.prefix["a"] == [pf.Str("A"), pf.RawInline("~", format="latex")]


def test_set_suffix():
    from panpdf.filters.crossref import Crossref

    crossref = Crossref()
    crossref.set_suffix("a", "A")
    assert crossref.suffix["a"] == [pf.Str("A")]
