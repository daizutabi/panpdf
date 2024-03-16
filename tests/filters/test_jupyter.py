from __future__ import annotations

from typing import TYPE_CHECKING

from panflute import Doc, Image

from panpdf.filters.jupyter import Jupyter

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_convert_image_base64(store: Store, image_factory):
    from panpdf.filters.jupyter import convert_image_base64

    image = image_factory("fig:png", "png.ipynb")
    data = store.get_data("fig:png", "png.ipynb")
    image = convert_image_base64(data, image)
    assert image.url.startswith("data:image/png;base64,iVBO")
    assert image.classes == ["panpdf-base64"]
    assert image.identifier == "fig:png"


def test_convert_image_pdf(store: Store, image_factory):
    from panpdf.filters.jupyter import convert_image_pdf

    image = image_factory("fig:pdf", "pdf.ipynb")
    data = store.get_data("fig:pdf", "pdf.ipynb")
    image = convert_image_pdf(data, image)
    assert image.url.startswith("JVBE")
    assert image.classes == ["panpdf-pdf"]


def test_convert_image_svg(store: Store, image_factory):
    from panpdf.filters.jupyter import convert_image_svg

    image = image_factory("fig:svg", "svg.ipynb")
    data = store.get_data("fig:svg", "svg.ipynb")
    image = convert_image_svg(data, image)
    assert image.url.startswith('<?xml version="1.0"')
    assert image.classes == ["panpdf-svg"]


def test_convert_image_pgf(store: Store, image_factory):
    from panpdf.filters.jupyter import convert_image_pgf

    image = image_factory("fig:pgf", "pgf.ipynb")
    data = store.get_data("fig:pgf", "pgf.ipynb")
    image = convert_image_pgf(data, image)
    assert image.url.startswith("%% Creator: Matplotlib")
    assert image.classes == ["panpdf-pgf"]


def test_convert_image(store: Store, image_factory):
    from panpdf.filters.jupyter import convert_image

    image = image_factory("fig:pgf", "pgf.ipynb")
    data = store.get_data("fig:pgf", "pgf.ipynb")
    image = convert_image(data, image)
    assert image.url.startswith("%% Creator: Matplotlib")
    assert image.classes == ["panpdf-pgf"]


def test_image_pgf(store, image_factory, fmt):
    jupyter = Jupyter(store=store)
    doc = Doc()
    image = image_factory(f"fig:{fmt}", f"{fmt}.ipynb")
    image = jupyter.action(image, doc)
    assert isinstance(image, Image)
    match fmt:
        case "pgf":
            assert image.url.startswith("%% Creator: Matplotlib")
        case "png":
            assert image.url.startswith("data:image/png;base64,iVBOR")
        case "pdf":
            assert image.url.startswith("JVBERi0xLjQKJazcIKu6C")
        case "svg":
            assert image.url.startswith('<?xml version="1.0"')
