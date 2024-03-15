import panflute as pf


def test_image():
    text = "![caption 1](a.png){#id .cls1 .cls2 k1=v1 k2=100}"
    elems = pf.convert_text(text)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, pf.Para)
    image = para.content[0]
    assert isinstance(image, pf.Image)
    assert pf.stringify(image) == "caption 1"
    assert image.identifier == "id"
    assert image.classes == ["cls1", "cls2"]
    assert image.attributes["k1"] == "v1"
    assert image.attributes["k2"] == "100"


def test_image_caption_cite():
    text = "![caption [@fig:b].](a.png){#fig:a}"
    elems = pf.convert_text(text)
    image = elems[0].content[0]  # type:ignore
    assert isinstance(image, pf.Image)
    cite = image.content[2]
    assert isinstance(cite, pf.Cite)
    assert cite.citations[0].id == "fig:b"  # type:ignore


def test_image_caption_math():
    text = "![caption $x$.](a.png){#fig:a}"
    elems = pf.convert_text(text)
    image = elems[0].content[0]  # type:ignore
    assert isinstance(image, pf.Image)
    math = image.content[2]
    assert isinstance(math, pf.Math)
    assert math.text == "x"
    assert math.format == "InlineMath"
