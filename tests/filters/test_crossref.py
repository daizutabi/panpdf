import inspect

import panflute as pf
import pytest
from panflute import Doc


@pytest.mark.parametrize("lang", ["ja", "en"])
def test_run_ja(lang):
    from panpdf.filters.crossref import Crossref

    text = """
    [@sec:section] [@sec:subsection]
    [@fig:pgf] [@fig:png] [@fig:pdf]
    [@tbl:markdown]
    [@eq:markdown]
    [@abc]
    """
    doc = pf.convert_text(inspect.cleandoc(text), standalone=True)
    assert isinstance(doc, Doc)
    crossref = Crossref(language=lang)
    doc = crossref.run(doc)
    tex = pf.convert_text(doc, input_format="panflute", output_format="latex")
    if lang == "ja":
        for ref in [
            "\\ref{sec:section}",
            "図~\\ref{fig:pgf}",
            "図~\\ref{fig:pdf}",
            "図~\\ref{fig:png}",
            "表~\\ref{tbl:markdown}",
            "式~\\ref{eq:markdown}",
            "{[}@abc{]}",
        ]:
            assert ref in tex  # type:ignore
    else:
        for ref in [
            "\\ref{sec:section}",
            "Fig.~\\ref{fig:pgf}",
            "Fig.~\\ref{fig:pdf}",
            "Fig.~\\ref{fig:png}",
            "Table~\\ref{tbl:markdown}",
            "Eq.~\\ref{eq:markdown}",
            "{[}@abc{]}",
        ]:
            assert ref in tex  # type:ignore
