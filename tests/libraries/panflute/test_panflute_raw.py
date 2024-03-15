import panflute as pf
from panflute import Math, Para, RawInline, Space, Str, Table

from panpdf.filters.attributes import Attributes


def test_figure():
    text = "![caption  $\\sqrt{2}$](a.png){#fig:id}"
    para = pf.convert_text(text)[0]  # type:ignore
    para = Para(*para.content)  # type:ignore
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    lines = [
        "\\begin{figure}",
        "\\hypertarget{fig:id}{%",
        "\\centering",
        "\\includegraphics{a.png}",
        "\\caption{caption \\(\\sqrt{2}\\)}\\label{fig:id}",
        "}",
        "\\end{figure}",
    ]
    assert tex == "\n".join(lines)


def test_table():
    text = "|a|a|\n|-|-|\n|1|2|\n: caption {#tbl:id}"
    table = pf.convert_text(text)[0]  # type:ignore
    assert isinstance(table, Table)
    Attributes().action(table, None)
    assert pf.stringify(table.caption) == "caption"
    tex = pf.convert_text(table, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    lines = tex.split("\n")
    assert lines[0] == "\\begin{longtable}[]{@{}ll@{}}"
    # assert lines[1] == "\\caption{caption}\\label{tbl:id}\\tabularnewline"
    assert "\\caption{caption}" in lines[1]
    assert "\\tabularnewline" in lines[1]


def test_raw():
    r1 = RawInline("\\begin{env}", format="latex")
    r2 = RawInline("\\end{env}", format="latex")
    text = "![caption](a.png){#fig:id}"
    elems = pf.convert_text(text)
    para = Para(r1, *elems[0].content, r2)  # type:ignore
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    assert tex == "\\begin{env}\\includegraphics{a.png}\\end{env}"


def test_raw_elements():
    begin = RawInline("\\begin{env}\n", format="latex")
    end = RawInline("\\end{env}\n", format="latex")
    s = Str("abc")
    m = Math("x=1", format="InlineMath")
    para = Para(begin, begin, s, Space(), m, end, end)
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    a = "\\begin{env}\n\\begin{env}\nabc \\(x=1\\)\\end{env}\n\\end{env}"
    assert tex == a
