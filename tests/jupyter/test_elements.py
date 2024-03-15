from __future__ import annotations

from typing import TYPE_CHECKING

import panflute as pf
import pytest
from panflute import Image, Math, Table

if TYPE_CHECKING:
    from panpdf.jupyter.stores import Store


def test_convert_image_to_code_block(store: Store, image_factory, fmt: str):
    from panpdf.jupyter.elements import convert_image_to_code_block

    id_ = f"fig:{fmt}"
    path = f"{fmt}.ipynb"
    image = image_factory(id_, path)
    source = store.get_source(id_, path)
    block = convert_image_to_code_block(source, image)
    assert block.text.rstrip() == "import matplotlib.pyplot as plt\n\nplt.plot([-1, 0, 1])"
    assert block.classes == ["python"]
    assert block.identifier == f"fig:{fmt}"


# def test_convert_image_base64(store: Store, image_factory):
#     from panpdf.jupyter.elements import convert_image_base64

#     image = image_factory("fig:png", "png.ipynb")
#     data = store.get_data("fig:png", "png.ipynb")
#     image = convert_image_base64(data, image)
#     assert image.url.startswith("data:image/png;base64,iVBO")
#     assert image.classes == ["panpdf-base64"]
#     assert image.identifier == "fig:png"


# def test_convert_image_pdf(store: Store, image_factory):
#     from panpdf.jupyter.elements import convert_image_pdf

#     image = image_factory("fig:pdf", "pdf.ipynb")
#     data = store.get_data("fig:pdf", "pdf.ipynb")
#     image = convert_image_pdf(data, image)
#     assert image.url.startswith("JVBE")
#     assert image.classes == ["panpdf-pdf"]


# def test_convert_image_svg(store: Store, image_factory):
#     from panpdf.jupyter.elements import convert_image_svg

#     image = image_factory("fig:svg", "svg.ipynb")
#     data = store.get_data("fig:svg", "svg.ipynb")
#     image = convert_image_svg(data, image)
#     assert image.url.startswith('<?xml version="1.0"')
#     assert image.classes == ["panpdf-svg"]


# def test_convert_image_pgf(store: Store, image_factory):
#     from panpdf.jupyter.elements import convert_image_pgf

#     image = image_factory("fig:pgf", "pgf.ipynb")
#     data = store.get_data("fig:pgf", "pgf.ipynb")
#     image = convert_image_pgf(data, image)
#     assert image.url.startswith("%% Creator: Matplotlib")
#     assert image.classes == ["panpdf-pgf"]


# def test_convert_image(store: Store, image_factory):
#     from panpdf.jupyter.elements import convert_image

#     image = image_factory("fig:pgf", "pgf.ipynb")
#     data = store.get_data("fig:pgf", "pgf.ipynb")
#     image = convert_image(data, image)
#     assert image.url.startswith("%% Creator: Matplotlib")
#     assert image.classes == ["panpdf-pgf"]
