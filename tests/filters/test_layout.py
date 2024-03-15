from pathlib import Path

import panflute as pf
from panflute import Cite, Doc, Image, Math, Para, RawInline, Space, Span, Str

import panpdf.filters.layout as L  # noqa: N812
from panpdf.filters.attributes import Attributes
from panpdf.filters.jupyter import Jupyter


def convert_to_para(text: str) -> Para:
    return Attributes().run(text).content[0]  # type:ignore


def test_convert_math_equation():
    para = convert_to_para("$$x=1$$ {#id}")
    span = para.content[0]
    assert isinstance(span, Span)
    math = span.content[0]
    assert isinstance(math, Math)
    m = L.convert_math(math)
    assert isinstance(m, RawInline)
    assert isinstance(m.text, str)
    text = "\\begin{equation}\nx=1\\label{id}\n\\end{equation}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math_eqnarray():
    text = "$$x=1\\\\\ny=2$$ {#id}"
    math = convert_to_para(text).content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = L.convert_math(math)
    text = "\\begin{eqnarray}\nx=1\\\\\ny=2\\label{id}\n\\end{eqnarray}\n"
    assert m.text == text
    assert m.format == "latex"


def test_convert_math():
    math = convert_to_para("$$x=1$$").content[0].content[0]  # type:ignore
    assert isinstance(math, Math)
    m = L.convert_math(math)
    assert isinstance(m, Math)


def test_convert_table():
    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = pf.convert_text(text)[0]  # type:ignore
    Attributes().action(table, None)  # type:ignore
    table = L.convert_table(table)  # type:ignore
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert "\\caption{\\label{tbl:id}caption}" in tex  # type:ignore


def test_split_images_caption_nofigure():
    para = convert_to_para("a b c")
    images, caption = L.split_images_caption(para)
    assert not images
    assert caption is None


def test_split_images_caption_figure():
    text = "![caption $\\sqrt{2}$](a.png){#fig:id width=10cm}"
    para = convert_to_para(text)
    images, caption = L.split_images_caption(para)
    assert images[0].content[0] == Str("caption")
    assert isinstance(images[0].content[2], Math)
    assert caption is None


def test_split_images_caption_minifigure():
    text = "![caption $a$](a.png){#fig:a}![$b$ text](b.png){#fig:b}"
    para = convert_to_para(text)
    images, caption = L.split_images_caption(para)
    assert isinstance(images[1].content[0], Math)
    assert images[1].content[2] == Str("text")
    assert caption is None


def test_split_images_caption_minifigure_softbreak():
    text = "![caption $a$](a.png){#fig:a}\n![caption $b$](b.png){#fig:b}"
    para = convert_to_para(text)
    images, caption = L.split_images_caption(para)
    assert images[1].content[0] == Str("caption")
    assert isinstance(images[1].content[2], Math)
    assert caption is None


def test_split_images_caption_subfigure():
    text = "![a $a$](a.png){#fig:a}\n![b $b$](b.png){#fig:b}\n"
    text += ": caption $x=1$ {#fig:c .cls width=1cm}"
    para = convert_to_para(text)
    images, caption = L.split_images_caption(para)
    assert isinstance(images[1].content[2], Math)
    assert isinstance(caption, list)
    assert caption[0] == Str("caption")
    assert caption[1] == Space()
    assert isinstance(caption[2], Math)
    assert caption[4] == Str("{#fig:c")


def R(text):  # noqa: N802
    return RawInline(text, format="latex")


def test_convert_para_figure():
    text = "![caption $\\sqrt{2}$ [@cite]](a.png){#fig:id width=10cm}"
    para = convert_to_para(text)
    para_ref = pf.convert_text(text)[0]  # type:ignore
    assert para == para_ref
    para = L.convert_para(para)
    assert para.content[0] == R("\\begin{figure}\n\\centering\n")
    assert para.content[1] == R("\\centering\n\\includegraphics[width=10cm]{a.png}%\n")
    span = para.content[2]
    assert isinstance(span, Span)
    assert span.content[0] == RawInline("\\caption{", format="latex")
    assert span.content[1] == Str("caption")
    assert span.content[3] == Math("\\sqrt{2}", format="InlineMath")
    assert isinstance(span.content[5], Cite)
    assert span.content[6] == R("}\\label{fig:id}\n")
    assert span.identifier == "fig:id"
    assert para.content[3] == R("\\end{figure}\n")
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\protect\\hypertarget{fig:id}{}{\\caption{caption \\(\\sqrt{2}\\)" in tex


def test_figure_minipage():
    text = (
        "![caption $x$ [@a].](a.png){#fig:id1 width=40% hspace=1cm}\n"
        "![caption $y$ [@b].](b.png){#fig:id2 width=60%}"
    )
    para = convert_to_para(text)
    image = para.content[0]
    assert isinstance(image, Image)
    image = para.content[2]
    assert isinstance(image, Image)
    para = L.convert_para(para)
    assert para.content[0] == R("\\begin{figure}\n\\centering\n")
    assert para.content[1] == R("\\begin{minipage}[t]{0.4\\columnwidth}\n")
    assert para.content[2] == R("\\centering\n\\includegraphics{a.png}%\n")
    span = para.content[3]
    assert isinstance(span, Span)
    assert span.content[0] == RawInline("\\caption{", format="latex")
    assert span.content[1] == Str("caption")
    assert isinstance(span.content[3], Math)
    assert isinstance(span.content[5], Cite)
    assert span.content[6] == Str(".")
    assert span.content[7] == R("}\\label{fig:id1}\n")
    assert para.content[4] == R("\\end{minipage}%\n")
    assert para.content[5] == R("\\hspace{1cm}%\n")
    assert para.content[6] == R("\\begin{minipage}[t]{0.6\\columnwidth}\n")


def test_create_suffix():
    text = "![a $a$](a.png){#fig:a}\n![b $b$](b.png){#fig:b}\n"
    text += ": caption $x=1$ [@cite]. {#fig:c}"
    para = convert_to_para(text)
    _, caption = L.split_images_caption(para)
    assert caption is not None
    suffix = L.create_suffix(caption)
    assert isinstance(suffix, Span)
    assert isinstance(suffix.content[0], RawInline)
    assert suffix.content[1] == Str("caption")
    assert suffix.content[3] == Math("x=1", format="InlineMath")
    assert isinstance(suffix.content[5], Cite)
    assert suffix.content[6] == Str(".")
    assert isinstance(suffix.content[7], RawInline)
    assert suffix.identifier == "fig:c"


def test_figure_subfigure():
    text = "![a $a$](a.png){#fig:a hspace=3cm}\n![b $b$](b.png){#fig:b}\n"
    text += ": caption $x=1$ [@cite]. {#fig:c}"
    para = convert_to_para(text)
    para = L.convert_para(para)
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    l = tex.split("\n")  # noqa: E741
    assert l[0] == "\\begin{figure}"
    assert l[1] == "\\centering"
    assert l[2] == "\\begin{subfigure}[t]{0.5\\columnwidth}"
    assert l[3] == "\\centering"
    assert l[4] == "\\includegraphics{a.png}%"
    p = "\\protect\\hypertarget{fig:a}{}{\\caption{a \\(a\\)}\\label{fig:a}"
    assert l[5] == p
    assert l[6] == "}\\end{subfigure}%"
    assert l[7] == "\\hspace{3cm}%"
    assert l[-2] == "{[}@cite{]}.}\\label{fig:c}"
    assert l[-1] == "}\\end{figure}"


def test_figure_latex(store):
    text = "![pgf](pgf.ipynb){#fig:pgf}"
    para = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(para, Para)
    para = Jupyter(store=store).action(para, Doc())[0]  # type:ignore
    assert isinstance(para, Para)
    image = para.content[0]
    assert isinstance(image, Image)
    assert "panpdf-pgf" in image.classes
    para = L.convert_para(para)
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    assert "\\centering\n%% Creator" in tex  # type:ignore


def test_prepare():
    paths = [Path(p) for p in ["_lualatex", "standalone.tex"]]
    # for path in paths:
    #     assert not path.exists()
    layout = L.Layout(external=True)
    delete = layout.prepare(None)  # type:ignore
    for path in paths:
        assert path.exists()
    delete()
    for path in paths:
        assert not path.exists()
    if (path := Path("_images")).exists():
        path.rmdir()
