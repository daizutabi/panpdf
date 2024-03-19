from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from panflute import Doc, Image

from panpdf.filters.jupyter import Jupyter

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_create_image_file_base64(store: Store):
    from panpdf.filters.jupyter import create_image_file_base64

    data = store.get_data("png.ipynb", "fig:png")
    text = data["image/png"]
    path = create_image_file_base64(text, ".png")
    assert os.path.exists(path)


def test_create_image_file_svg(store: Store):
    from panpdf.filters.jupyter import create_image_file_svg

    data = store.get_data("svg.ipynb", "fig:svg")
    xml = data["image/svg+xml"]
    url, text = create_image_file_svg(xml)
    assert Path(url).exists()
    assert Path(url).stat().st_size
    assert text.startswith("JVBER")


def test_create_defaults_for_standalone(defaults):
    from panpdf.filters.jupyter import create_defaults_for_standalone

    path = create_defaults_for_standalone(defaults)
    assert path.exists()

    with path.open(encoding="utf8") as f:
        defaults = yaml.safe_load(f)

    for toc in ["table-of-contents", "toc", "toc-depth"]:
        if toc in defaults:
            del defaults[toc]

    variables = defaults["variables"]
    assert variables["documentclass"] == "standalone"
    options = variables["classoption"]
    assert "class=jlreq" in options


def test_create_defaults_for_standalone_none():
    from panpdf.filters.jupyter import create_defaults_for_standalone

    path = create_defaults_for_standalone()
    assert path.exists()

    with path.open(encoding="utf8") as f:
        defaults = yaml.safe_load(f)

    assert defaults["variables"] == {"documentclass": "standalone"}
    assert defaults["include-in-header"].endswith(".tex")


def test_create_image_file_pgf(store: Store, defaults):
    from panpdf.filters.jupyter import create_image_file_pgf

    data = store.get_data("pgf.ipynb", "fig:pgf")
    text = data["text/plain"]
    url, text = create_image_file_pgf(text, defaults)
    assert Path(url).exists()
    assert Path(url).stat().st_size
    assert text.startswith("JVBER")


def test_create_image_file_pgf_none(store: Store):
    from panpdf.filters.jupyter import create_image_file_pgf

    data = store.get_data("pgf.ipynb", "fig:pgf")
    text = data["text/plain"]
    url, text = create_image_file_pgf(text)
    assert Path(url).exists()
    assert Path(url).stat().st_size
    assert text.startswith("JVBER")


@pytest.mark.parametrize("standalone", [False, True])
def test_jupyter(store: Store, image_factory, defaults, fmt, standalone):
    if fmt == "pgf":
        store.delete_data(f"{fmt}.ipynb", f"fig:{fmt}", "application/pdf")
        data = store.get_data(f"{fmt}.ipynb", f"fig:{fmt}")
        assert "image/png" in data
        assert "text/plain" in data
        assert "application/pdf" not in data

    jupyter = Jupyter(defaults, standalone=standalone, store=store)

    doc = Doc()
    image = image_factory(f"{fmt}.ipynb", f"fig:{fmt}")
    image = jupyter.action(image, doc)
    assert isinstance(image, Image)
    if fmt == "pgf" and not standalone:
        assert image.url.startswith("%%")
    else:
        fmt_ = fmt.replace("pgf", "pdf").replace("svg", "pdf")
        assert image.url.endswith(f".{fmt_}")
        assert Path(image.url).exists()
        assert Path(image.url).stat().st_size

    if fmt == "pgf":
        data = store.get_data(f"{fmt}.ipynb", f"fig:{fmt}")
        assert "image/png" in data
        assert "text/plain" in data
        if standalone:
            assert "application/pdf" in data
        else:
            assert "application/pdf" not in data

        store.delete_data(f"{fmt}.ipynb", f"fig:{fmt}", "application/pdf")

        data = store.get_data(f"{fmt}.ipynb", f"fig:{fmt}")
        assert "image/png" in data
        assert "text/plain" in data
        assert "application/pdf" not in data
