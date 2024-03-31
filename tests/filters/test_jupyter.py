from __future__ import annotations

import platform
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from panflute import Doc, Image, Str

from panpdf.filters.jupyter import Jupyter

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_create_image_file_base64(store: Store):
    from panpdf.filters.jupyter import create_image_file_base64

    data = store.get_data("png.ipynb", "fig:png")
    text = data["image/png"]
    file = create_image_file_base64(text, ".png")
    path = Path(file)
    assert path.exists()
    assert path.stat().st_size


def test_create_image_file_svg(store: Store):
    from panpdf.filters.jupyter import create_image_file_svg

    data = store.get_data("svg.ipynb", "fig:svg")
    xml = data["image/svg+xml"]
    try:
        url, text = create_image_file_svg(xml)
    except OSError:
        if platform.system() == "Windows":
            return

        raise

    path = Path(url)
    assert path.exists()
    assert path.stat().st_size
    assert text.startswith("JVBER")


def test_create_image_file_none():
    from panpdf.filters.jupyter import create_image_file

    assert create_image_file({}) is None


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
    header = defaults["include-in-header"]
    assert isinstance(header, list)
    assert isinstance(header[0], str)
    assert header[0].endswith(".tex")


@pytest.mark.parametrize("use_defaults", [False, True])
def test_create_image_file_pgf(store: Store, defaults, use_defaults):
    from panpdf.filters.jupyter import create_image_file_pgf

    data = store.get_data("pgf.ipynb", "fig:pgf")
    text = data["text/plain"]
    defaults = defaults if use_defaults else None
    url, text = create_image_file_pgf(text, defaults)

    path = Path(url)
    assert path.exists()
    assert path.stat().st_size
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

    try:
        image = jupyter.action(image, doc)
    except OSError:
        if fmt == "svg" and platform.system() == "Windows":
            return

        raise

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


def test_jupyter_action():
    from panpdf.filters.jupyter import Jupyter

    doc = Doc()
    jupyter = Jupyter()
    image = Image(Str("a"), url="a.png")
    assert jupyter.action(image, doc) is image


def test_jupyter_action_error():
    from panpdf.filters.jupyter import Jupyter

    doc = Doc()
    jupyter = Jupyter()
    image = Image(Str("a"), url="a.ipynb", identifier="a")
    with pytest.raises(ValueError, match=r"\[panpdf\] Unknown"):
        jupyter.action(image, doc)
