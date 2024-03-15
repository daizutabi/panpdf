import panflute as pf
import pytest

from panpdf.filters.latex import Latex


@pytest.mark.parametrize(("a", "b"), [(" ", " "), ("\n", ""), ("   ", "\n")])
def test_latex_crossref(a, b):
    text = f"\\noindent{a}[@ref]{b}abc"
    rawinline = pf.convert_text(text)[0].content[0]  # type:ignore
    assert isinstance(rawinline, pf.RawInline)
    elems = Latex().action(rawinline, None)  # type:ignore
    assert isinstance(elems, list)
    assert elems[1] == pf.Space()
    assert elems[2] == pf.Cite(pf.Str("[@ref]"))
    if len(elems) == 4:
        assert elems[3] == pf.Space()
