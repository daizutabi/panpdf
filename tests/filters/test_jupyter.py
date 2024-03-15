from __future__ import annotations

from panflute import Doc, Image, Para, Space, Str
from panflute.elements import CodeBlock

from panpdf.filters.jupyter import Jupyter


def test_image(store, image_factory):
    jupyter = Jupyter(store=store)
    doc = Doc()
    image = image_factory("fig:pgf", "pgf.ipynb")
    elems = jupyter.action(Para(Str("abd"), Space(), image, Space(), Str("def")), doc)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    assert isinstance(para.content[0], Str)
    assert isinstance(para.content[1], Space)
    image = para.content[2]
    assert isinstance(image, Image)
    assert image.url.startswith("%% Creator: Matplotlib")


def test_image_to_code_block(store, image_factory):
    jupyter = Jupyter(store=store)
    doc = Doc()
    image = image_factory("fig:pgf", "pgf.ipynb")
    assert isinstance(image, Image)
    image.classes += ["source"]
    elems = jupyter.action(Para(image), doc)
    assert isinstance(elems, list)
    code_block = elems[0]
    assert isinstance(code_block, CodeBlock)
    assert "python" in code_block.classes
