import panflute as pf


def test_math_inline():
    text = "$a = 1$"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, pf.Para)
    math = para.content[0]
    assert isinstance(math, pf.Math)
    assert math.text == "a = 1"
    assert math.format == "InlineMath"
    assert not hasattr(math, "identifier")
    assert not hasattr(math, "classes")
    assert not hasattr(math, "attributes")


def test_math_block():
    text = "ab\n$$a = 1$$ {#id .cls1 k1=v1}\ncd"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, pf.Para)
    assert isinstance(para.content[1], pf.SoftBreak)
    math = para.content[2]
    assert isinstance(math, pf.Math)
    assert math.format == "DisplayMath"
    assert isinstance(para.content[3], pf.Space)
    str_ = para.content[4]
    assert isinstance(str_, pf.Str)
    assert str_.text == "{#id"
    assert not hasattr(math, "identifier")
    assert not hasattr(math, "classes")
    assert not hasattr(math, "attributes")


def test_math_block_para():
    text = "ab\n\n$$a = 1$$ {#id .cls1 k1=v1}\n\ncd"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[1]
    assert isinstance(para, pf.Para)
    assert len(para.content) == 7
    math = para.content[0]
    assert isinstance(math, pf.Math)
    assert math.format == "DisplayMath"
    assert isinstance(para.content[1], pf.Space)
    str_ = para.content[2]
    assert isinstance(str_, pf.Str)
    assert str_.text == "{#id"


def test_math_latex():
    text = "ab\n\n$$a = 1$$\n\ncd"
    tex = pf.convert_text(text, output_format="latex")
    assert tex == "ab\n\n\\[a = 1\\]\n\ncd"
