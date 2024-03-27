import panflute as pf


def test_code():
    text = "`a = 1`{.python #id k1=v1}"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, pf.Para)
    code = para.content[0]
    assert isinstance(code, pf.Code)
    assert code.text == "a = 1"
    assert code.identifier == "id"
    assert code.classes == ["python"]
    assert code.attributes["k1"] == "v1"


def test_code_block():
    text = "```{.python #id k1=v1}\na = 1\n```\n"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    code = elems[0]
    assert isinstance(code, pf.CodeBlock)
    assert code.text == "a = 1"
    assert code.identifier == "id"
    assert code.classes == ["python"]
    assert code.attributes["k1"] == "v1"


def test_code_block_attr():
    text = "```python {#id .input k1=v1}\na = 1\n```"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    code = elems[0]
    assert isinstance(code, pf.CodeBlock)
    assert code.text == "a = 1"
    assert code.identifier == "id"
    assert code.classes == ["python", "input"]
    assert code.attributes["k1"] == "v1"


def test_code_block_latex():
    text = "```python {numbers=left}\na = 1\n```"
    t = pf.convert_text(text, output_format="latex")
    assert isinstance(t, str)
    assert "\\begin{Shaded}" in t
    assert "\\begin{Highlighting}[]" in t
