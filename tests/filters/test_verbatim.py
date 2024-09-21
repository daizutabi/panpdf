import panflute as pf
from panflute import CodeBlock, Doc


def test_create_title():
    from panpdf.filters.verbatim import create_title

    code = CodeBlock("a=1", attributes={"title": "Title"})
    elems = create_title(code)
    text = pf.convert_text(elems, input_format="panflute", output_format="latex")
    assert isinstance(text, str)
    assert "formatcom=\\color{NavyBlue}\\bfseries" in text
    assert "\\NormalTok{Title}" in text
    assert "\\NormalTok{a=1}" in text


def test_create_code_block():
    from panpdf.filters.verbatim import create_code_block

    code = CodeBlock("a=1")
    elems = create_code_block(code, (0.1, 0.2, 0.3))
    assert elems[1] is code
    assert code.classes == ["text"]


def test_define_verbatim_environment():
    from panpdf.filters.verbatim import CONFIG, define_verbatim_environment

    config = CONFIG.copy()
    text = define_verbatim_environment({"fontsize": "\\large"})
    assert text.endswith(r"{commandchars=\\\{\},fontsize=\large}")
    text = define_verbatim_environment({"a": "b"})
    assert text.endswith(r"a=b,fontsize=\large}")
    CONFIG.update(config)
    text = define_verbatim_environment({})
    assert text.endswith(r"{commandchars=\\\{\},fontsize=\small}")


def test_define_shade_color():
    from panpdf.filters.verbatim import define_shade_color

    text = define_shade_color((0.2, 0.3, 0.5))
    assert text == "\\definecolor{shadecolor}{rgb}{0.2,0.3,0.5}"


def test_create_header():
    from panpdf.filters.verbatim import create_header

    path = create_header()
    assert path.exists()
    text = path.read_text("utf-8")
    assert text.startswith("\\ifdefined\\Shaded")
    assert "\\linespread" in text

    path = create_header(2)
    text = path.read_text("utf-8")
    assert "\\linespread{2}}" in text


def test_verbatim_output():
    from panpdf.filters.verbatim import Verbatim

    verbatim = Verbatim()
    assert not verbatim.shaded

    text = "```python\n1\n```\n\n```python {.output}\n1\n```"
    doc = verbatim.run(text)
    assert isinstance(doc, Doc)
    assert verbatim.shaded

    t = pf.convert_text(
        doc, input_format="panflute", output_format="latex", standalone=True,
    )
    assert isinstance(t, str)
    assert "\\vspace{-0.5\\baselineskip}" in t


def test_verbatim_title():
    from panpdf.filters.verbatim import Verbatim

    verbatim = Verbatim()
    assert not verbatim.shaded

    text = "```python\n1\n```\n\n```python {title=Title}\n1\n```"
    doc = verbatim.run(text)
    assert isinstance(doc, Doc)
    assert verbatim.shaded

    t = pf.convert_text(
        doc, input_format="panflute", output_format="latex", standalone=True,
    )
    assert isinstance(t, str)
    assert "formatcom=\\color{NavyBlue}\\bfseries" in t
    assert "\\NormalTok{Title}" in t
    assert "\\DecValTok{1}" in t
