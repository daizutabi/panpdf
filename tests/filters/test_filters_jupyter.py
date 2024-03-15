from panflute import Doc, Image, Math, Para, Space, Str
from panflute.elements import CodeBlock

from panpdf.filters.jupyter import Jupyter


def test_jupyter_image(store, image_factory):
    jupyter = Jupyter(store=store)
    doc = Doc()
    id = "fig:tikz"  # noqa: A001
    path = "tests/test.ipynb"
    image: Image = image_factory(id, path)
    elems = jupyter.action(Para(Str("abc"), Space(), image, Space(), Str("def")), doc)
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    image = para.content[2]  # type: ignore
    assert isinstance(image, Image)
    assert image.url.startswith("\\begin")
    s = para.content[4]
    assert isinstance(s, Str)
    assert s.text == "def"


def test_jupyter_image_to_code_block(store, image_factory):
    jupyter = Jupyter(store=store)
    doc = Doc()
    id = "fig:tikz"  # noqa: A001
    path = "tests/test.ipynb"
    image: Image = image_factory(id, path)
    image.classes += ["source"]
    elems = jupyter.action(Para(image), doc)
    assert isinstance(elems, list)
    code_block = elems[0]
    assert isinstance(code_block, CodeBlock)
    assert "python" in code_block.classes


def test_jupyter_math(store, math_factory):
    jupyter = Jupyter(store=store)
    doc = Doc()
    id = "eq:sympy"  # noqa: A001
    math = math_factory(id)
    assert isinstance(math, Math)
    math = jupyter.action(math, doc)
    assert isinstance(math, Math)
