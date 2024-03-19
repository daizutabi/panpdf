from __future__ import annotations

import os
import shutil
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

    if not shutil.which("lualatex"):
        return

    data = store.get_data("pgf.ipynb", "fig:pgf")
    text = data["text/plain"]
    url, text = create_image_file_pgf(text, defaults)
    assert Path(url).exists()
    assert text.startswith("JVBER")


@pytest.mark.parametrize("standalone", [False, True])
def test_jupyter_png(store: Store, image_factory, defaults, fmt, standalone):
    if not shutil.which("lualatex"):
        return

    if fmt == "svg":
        return

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

    if fmt == "pgf":
        store.delete_data(f"{fmt}.ipynb", f"fig:{fmt}", "application/pdf")
