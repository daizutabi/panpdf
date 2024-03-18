from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from panflute import Doc, Image, Plain, RawInline

from panpdf.filters.jupyter import Jupyter

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_create_image_file_base64(store: Store):
    from panpdf.filters.jupyter import create_image_file_base64

    data = store.get_data("png.ipynb", "fig:png")
    text = data["image/png"]
    path = create_image_file_base64(text, ".png")
    assert os.path.exists(path)


@pytest.fixture
def defaults():
    path = Path("examples/defaults.yaml")
    assert path.exists()
    return path


def test_create_defaults_for_standalone(defaults):
    from panpdf.filters.jupyter import create_defaults_for_standalone

    path = create_defaults_for_standalone(defaults)
    assert path.exists()

    with path.open(encoding="utf8") as f:
        defaults = yaml.safe_load(f)

    variables = defaults["variables"]
    assert variables["documentclass"] == "standalone"
    options = variables["classoption"]
    assert "class=jlreq" in options


def test_create_image_file_pgf(store: Store, defaults):
    from panpdf.filters.jupyter import create_image_file_pgf

    data = store.get_data("pgf.ipynb", "fig:pgf")
    text = data["text/plain"]
    url, text = create_image_file_pgf(text, defaults)
    assert Path(url).exists()
    assert text.startswith("JVBER")


@pytest.mark.parametrize("standalone", [False, True])
def test_jupyter_png(store: Store, image_factory, defaults, fmt, standalone):
    if fmt == "svg":
        return

    if fmt == "pgf":
        store.delete_data(f"{fmt}.ipynb", f"fig:{fmt}", "application/pdf")

    jupyter = Jupyter(defaults, standalone=standalone, store=store)

    doc = Doc()
    image = image_factory(f"{fmt}.ipynb", f"fig:{fmt}")
    image = jupyter.action(image, doc)
    assert isinstance(image, Image)
    if fmt == "pgf" and not standalone:
        assert image.url.startswith("%%")
    else:
        fmt_ = fmt.replace("pgf", "pdf")
        assert image.url.endswith(f".{fmt_}")
        assert Path(image.url).exists()


#     image = image_factory("fig:pdf", "pdf.ipynb")
#     data = store.get_data("fig:pdf", "pdf.ipynb")
#     image = convert_image_pdf(data, image)
#     assert image.url.startswith("JVBE")
#     assert image.classes == ["panpdf-pdf"]


# def test_convert_image_svg(store: Store, image_factory):
#     from panpdf.filters.jupyter import convert_image_svg

#     image = image_factory("fig:svg", "svg.ipynb")
#     data = store.get_data("fig:svg", "svg.ipynb")
#     image = convert_image_svg(data, image)
#     assert image.url.startswith('<?xml version="1.0"')
#     assert image.classes == ["panpdf-svg"]


# def test_convert_image_pgf(store: Store, image_factory):
#     from panpdf.filters.jupyter import convert_image_pgf

#     image = image_factory("fig:pgf", "pgf.ipynb")
#     data = store.get_data("fig:pgf", "pgf.ipynb")
#     image = convert_image_pgf(data, image)
#     assert image.url.startswith("%% Creator: Matplotlib")
#     assert image.classes == ["panpdf-pgf"]


# def test_convert_image(store: Store, image_factory):
#     from panpdf.filters.jupyter import convert_image

#     image = image_factory("fig:pgf", "pgf.ipynb")
#     data = store.get_data("fig:pgf", "pgf.ipynb")
#     image = convert_image(data, image)
#     assert image.url.startswith("%% Creator: Matplotlib")
#     assert image.classes == ["panpdf-pgf"]


# def test_image_pgf(store, image_factory, fmt):
#     jupyter = Jupyter(store=store)
#     doc = Doc()
#     image = image_factory(f"fig:{fmt}", f"{fmt}.ipynb")
#     image = jupyter.action(image, doc)
#     assert isinstance(image, Image)
#     match fmt:
#         case "pgf":
#             assert image.url.startswith("%% Creator: Matplotlib")

#         case "png":
#             assert image.url.startswith("data:image/png;base64,iVBOR")

#         case "pdf":
#             assert image.url.startswith("JVBERi0xLjQKJazcIKu6C")

#         case "svg":
#             assert image.url.startswith('<?xml version="1.0"')
