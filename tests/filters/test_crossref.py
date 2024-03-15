import panflute as pf

from panpdf.filters.attributes import Attributes
from panpdf.filters.crossref import Crossref
from panpdf.filters.layout import Layout


def test_prepare(doc):
    crossref = Crossref()
    crossref._prepare(doc)  # noqa: SLF001
    for id in [  # noqa: A001
        "sec:section",
        "sec:subsection",
        "fig:pdf",
        "fig:png",
        "fig:pgf",
        "tbl:markdown",
        "eq:markdown",
    ]:
        assert id in crossref.identifiers


def test_run(doc):
    crossref = Crossref(language="ja")
    crossref._prepare(doc)  # noqa: SLF001
    doc = crossref.run(doc)
    tex = pf.convert_text(doc, input_format="panflute", output_format="latex")
    for ref in [
        "\\ref{sec:section}",
        "図~\\ref{fig:pgf}",
        "図~\\ref{fig:pdf}",
        "図~\\ref{fig:png}",
        "表~\\ref{tbl:markdown}",
        "式~\\ref{eq:markdown}",
    ]:
        assert ref in tex  # type:ignore


def test_subcaption():
    attributes = Attributes()
    layout = Layout()
    crossref = Crossref(language="en")
    text = "![c1](1.png){#fig:1}\n![c2](2.png){#fig:2}\n: c3 {#fig:3}\n\n"
    text += "[@fig:1], [@fig:2], [@fig:3]"
    doc = pf.convert_text(text, standalone=True)
    doc = attributes.run(doc)  # type:ignore
    doc = layout.run(doc)  # type:ignore
    doc = crossref.run(doc)
    tex = pf.convert_text(doc, input_format="panflute", output_format="latex")
    text = "Fig.~\\ref{fig:1}, Fig.~\\ref{fig:2}, Fig.~\\ref{fig:3}"
    assert text in tex  # type:ignore
