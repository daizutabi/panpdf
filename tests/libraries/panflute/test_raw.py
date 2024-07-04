import panflute as pf
from panflute import Math, Para, RawInline, Space, Str


def test_raw():
    r1 = RawInline("\\begin{env}", format="latex")
    r2 = RawInline("\\end{env}", format="latex")
    text = "![caption](a.png){#fig:id width=1cm height=1cm}"
    elems = pf.convert_text(text)
    para = Para(r1, elems[0].content[0].content[0], r2)  # type:ignore
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    assert tex == "\\begin{env}\\includegraphics[width=1cm,height=1cm]{a.png}\\end{env}"


def test_raw_elements():
    begin = RawInline("\\begin{env}\n", format="latex")
    end = RawInline("\\end{env}\n", format="latex")
    s = Str("abc")
    m = Math("x=1", format="InlineMath")
    para = Para(begin, begin, s, Space(), m, end, end)
    tex = pf.convert_text(para, input_format="panflute", output_format="latex")
    a = "\\begin{env}\n\\begin{env}\nabc \\(x=1\\)\\end{env}\n\\end{env}"
    assert tex == a
