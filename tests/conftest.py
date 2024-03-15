from __future__ import annotations

from pathlib import Path

import panflute as pf
import pytest
from panflute import Figure, Image

import panpdf
from panpdf.utils import set_asyncio_event_loop_policy

set_asyncio_event_loop_policy()


@pytest.fixture(scope="session")
def notebook_dir() -> Path:
    return Path(panpdf.__file__).parent.parent.parent / "tests/notebooks"


@pytest.fixture(scope="session")
def store(notebook_dir):
    from panpdf.jupyter.stores import Store

    return Store([notebook_dir])


@pytest.fixture(scope="session")
def figure_factory():
    def figure_factory(id_, url="", caption="caption") -> Figure:
        text = f"![{caption}]({url}){{#{id_}}}"
        elems = pf.convert_text(text)
        assert isinstance(elems, list)
        fig = elems[0]
        assert isinstance(fig, Figure)
        return fig

    return figure_factory


@pytest.fixture(scope="session")
def image_factory(figure_factory):
    from panpdf.filters.attribute import set_attributes_figure

    def image_factory(id_, url="", caption="caption") -> Image:
        fig = figure_factory(id_, url, caption)
        set_attributes_figure(fig)
        img = fig.content[0].content[0]
        assert isinstance(img, Image)
        return img

    return image_factory
