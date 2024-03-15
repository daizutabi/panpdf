import panflute as pf
from panflute import Image, Math, Table

import panpdf.jupyter.element as E  # noqa: N812
from panpdf.jupyter.nbformat import Store


def test_convert_image_to_code_block(store: Store, image_factory):
    id_ = "fig:matplotlib"
    path = "tests/test.ipynb"
    image: Image = image_factory(id_, path)
    source = store.get_source(id_, path)
    assert source
    block = E.convert_image_to_code_block(source, image)
    assert "plt.plot" in block.text
    assert "python" in block.classes


def test_convert_image_by_pdf(store: Store, image_factory):
    id_ = "fig:makie"
    path = "tests/makie.ipynb"
    image: Image = image_factory(id_, path)
    data = store.get_data(id_, path)
    assert data
    image = E.convert_image_by_pdf(data, image)
    assert image.url.startswith("JV")
    assert "panpdf-pdf" in image.classes


def test_convert_image_by_base64(store: Store, image_factory):
    id_ = "fig:matplotlib"
    path = "tests/test.ipynb"
    image: Image = image_factory(id_, path)
    data = store.get_data(id_, path)
    assert data
    image = E.convert_image_by_base64(data, image)
    assert "data:image/png;base64," in image.url
    assert "panpdf-base64" in image.classes


def test_convert_image_by_latex(store: Store, image_factory):
    id_ = "fig:tikz"
    image: Image = image_factory(id_)
    data = store.get_data(id_)
    assert data
    image = E.convert_image_by_latex(data, image)
    assert isinstance(image, Image)
    assert "panpdf-latex" in image.classes


def test_convert_image_to_table(store: Store, image_factory):
    id_ = "tbl:pandas"
    image: Image = image_factory(id_, caption="abc\ndef")
    data = store.get_data(id_)
    assert data
    table = E.convert_image_to_table(data, image)
    assert isinstance(table, Table)
    assert table.identifier == id_
    assert pf.stringify(table.caption) == "abc def"


def test_convert_math(store: Store, math_factory):
    id_ = "eq:sympy"
    math: Math = math_factory(id_)
    data = store.get_data(id_)
    assert data
    math = E.convert_math(data, math)
    assert isinstance(math, Math)
    assert math.text == "y = f{\\left(x \\right)}"
