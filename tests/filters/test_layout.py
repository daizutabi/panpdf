from pathlib import Path

import panflute as pf
from panflute import Cite, Doc, Image, Math, Para, RawInline, Space, Span, Str, Table

from panpdf.filters.attribute import Attribute
from panpdf.filters.jupyter import Jupyter


def _convert(text: str):
    return Attribute().run(text).content[0]  # type:ignore


def test_convert_math_equation():
    from panpdf.filters.layout import convert_math

    text = "$$x=1$$ {#id}"
    math = _convert(text).content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, RawInline)
    text = "\\begin{equation}\nx=1\\label{id}\n\\end{equation}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math_eqnarray():
    from panpdf.filters.layout import convert_math

    text = "$$x=1\\\\\ny=2$$ {#id}"
    math = _convert(text).content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, RawInline)
    text = "\\begin{eqnarray}\nx=1\\\\\ny=2\\label{id}\n\\end{eqnarray}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math():
    from panpdf.filters.layout import convert_math

    math = _convert("$$x=1$$").content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = convert_math(math)
    assert isinstance(m, Math)


def test_convert_table():
    from panpdf.filters.layout import convert_table

    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = _convert(text)
    assert isinstance(table, Table)
    Attribute().action(table, None)
    table = convert_table(table)
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert "\\caption{\\label{tbl:id}caption}" in tex  # type:ignore


# def R(text):  # noqa: N802
#     return RawInline(text, format="latex")


# def test_convert_para_figure():
#     text = "![caption $\\sqrt{2}$ [@cite]](a.png){#fig:id width=10cm}"
#     para = _convert(text)
#     para_ref = pf.convert_text(text)[0]  # type:ignore
#     assert para == para_ref
#     para = L.convert_para(para)
#     assert para.content[0] == R("\\begin{figure}\n\\centering\n")
#     assert para.content[1] == R("\\centering\n\\includegraphics[width=10cm]{a.png}%\n")
#     span = para.content[2]
#     assert isinstance(span, Span)
#     assert span.content[0] == RawInline("\\caption{", format="latex")
#     assert span.content[1] == Str("caption")
#     assert span.content[3] == Math("\\sqrt{2}", format="InlineMath")
#     assert isinstance(span.content[5], Cite)
#     assert span.content[6] == R("}\\label{fig:id}\n")
#     assert span.identifier == "fig:id"
#     assert para.content[3] == R("\\end{figure}\n")
#     tex = pf.convert_text(para, input_format="panflute", output_format="latex")
#     assert isinstance(tex, str)
#     assert "\\protect\\hypertarget{fig:id}{}{\\caption{caption \\(\\sqrt{2}\\)" in tex


# def test_figure_minipage():
#     text = (
#         "![caption $x$ [@a].](a.png){#fig:id1 width=40% hspace=1cm}\n"
#         "![caption $y$ [@b].](b.png){#fig:id2 width=60%}"
#     )
#     para = _convert(text)
#     image = para.content[0]
#     assert isinstance(image, Image)
#     image = para.content[2]
#     assert isinstance(image, Image)
#     para = L.convert_para(para)
#     assert para.content[0] == R("\\begin{figure}\n\\centering\n")
#     assert para.content[1] == R("\\begin{minipage}[t]{0.4\\columnwidth}\n")
#     assert para.content[2] == R("\\centering\n\\includegraphics{a.png}%\n")
#     span = para.content[3]
#     assert isinstance(span, Span)
#     assert span.content[0] == RawInline("\\caption{", format="latex")
#     assert span.content[1] == Str("caption")
#     assert isinstance(span.content[3], Math)
#     assert isinstance(span.content[5], Cite)
#     assert span.content[6] == Str(".")
#     assert span.content[7] == R("}\\label{fig:id1}\n")
#     assert para.content[4] == R("\\end{minipage}%\n")
#     assert para.content[5] == R("\\hspace{1cm}%\n")
#     assert para.content[6] == R("\\begin{minipage}[t]{0.6\\columnwidth}\n")


# def test_create_suffix():
#     text = "![a $a$](a.png){#fig:a}\n![b $b$](b.png){#fig:b}\n"
#     text += ": caption $x=1$ [@cite]. {#fig:c}"
#     para = _convert(text)
#     _, caption = L.split_images_caption(para)
#     assert caption is not None
#     suffix = L.create_suffix(caption)
#     assert isinstance(suffix, Span)
#     assert isinstance(suffix.content[0], RawInline)
#     assert suffix.content[1] == Str("caption")
#     assert suffix.content[3] == Math("x=1", format="InlineMath")
#     assert isinstance(suffix.content[5], Cite)
#     assert suffix.content[6] == Str(".")
#     assert isinstance(suffix.content[7], RawInline)
#     assert suffix.identifier == "fig:c"


# def test_figure_subfigure():
#     text = "![a $a$](a.png){#fig:a hspace=3cm}\n![b $b$](b.png){#fig:b}\n"
#     text += ": caption $x=1$ [@cite]. {#fig:c}"
#     para = _convert(text)
#     para = L.convert_para(para)
#     tex = pf.convert_text(para, input_format="panflute", output_format="latex")
#     assert isinstance(tex, str)
#     l = tex.split("\n")  # noqa: E741
#     assert l[0] == "\\begin{figure}"
#     assert l[1] == "\\centering"
#     assert l[2] == "\\begin{subfigure}[t]{0.5\\columnwidth}"
#     assert l[3] == "\\centering"
#     assert l[4] == "\\includegraphics{a.png}%"
#     p = "\\protect\\hypertarget{fig:a}{}{\\caption{a \\(a\\)}\\label{fig:a}"
#     assert l[5] == p
#     assert l[6] == "}\\end{subfigure}%"
#     assert l[7] == "\\hspace{3cm}%"
#     assert l[-2] == "{[}@cite{]}.}\\label{fig:c}"
#     assert l[-1] == "}\\end{figure}"


# def test_figure_latex(store):
#     text = "![pgf](pgf.ipynb){#fig:pgf}"
#     para = pf.convert_text(text)[0]  # type:ignore
#     assert isinstance(para, Para)
#     para = Jupyter(store=store).action(para, Doc())[0]  # type:ignore
#     assert isinstance(para, Para)
#     image = para.content[0]
#     assert isinstance(image, Image)
#     assert "panpdf-pgf" in image.classes
#     para = L.convert_para(para)
#     tex = pf.convert_text(para, input_format="panflute", output_format="latex")
#     assert "\\centering\n%% Creator" in tex  # type:ignore


# def test_prepare():
#     paths = [Path(p) for p in ["_lualatex", "standalone.tex"]]
#     # for path in paths:
#     #     assert not path.exists()
#     layout = L.Layout(external=True)
#     delete = layout.prepare(None)  # type:ignore
#     for path in paths:
#         assert path.exists()
#     delete()
#     for path in paths:
#         assert not path.exists()
#     if (path := Path("_images")).exists():
#         path.rmdir()
