from __future__ import annotations

from pathlib import Path

import panflute as pf
import pytest
from nbstore import Store
from panflute import Figure, Image


@pytest.fixture(scope="session", autouse=True)
def _read_write():
    path = Path("tests/notebooks/pgf.ipynb")
    nb = path.read_text("utf-8")
    yield
    path.write_text(nb, "utf-8")


@pytest.fixture(scope="session", autouse=True)
def _clear_cache():
    from panpdf.filters.zotero import CSL_PATH

    yield
    CSL_PATH.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def notebook_dir() -> Path:
    return Path("tests/notebooks")


@pytest.fixture(scope="session")
def store(notebook_dir: Path):
    return Store(notebook_dir)


@pytest.fixture(scope="session")
def figure_factory():
    def figure_factory(url, identifier, caption="caption") -> Figure:
        text = f"![{caption}]({url}){{#{identifier}}}"
        elems = pf.convert_text(text)
        assert isinstance(elems, list)
        fig = elems[0]
        assert isinstance(fig, Figure)
        return fig

    return figure_factory


@pytest.fixture(scope="session")
def image_factory(figure_factory):
    from panpdf.filters.attribute import set_attributes_figure

    def image_factory(url, identifier, caption="caption") -> Image:
        fig = figure_factory(url, identifier, caption)
        set_attributes_figure(fig)
        img = fig.content[0].content[0]
        assert isinstance(img, Image)
        return img

    return image_factory


@pytest.fixture(params=["png", "pgf", "pdf", "svg"])
def fmt(request):
    return request.param
