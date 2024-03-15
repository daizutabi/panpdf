from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import panflute as pf
import pytest
from panflute import Image

import panpdf
from panpdf.utils import set_asyncio_event_loop_policy

if TYPE_CHECKING:
    from panflute import Image

set_asyncio_event_loop_policy()


@pytest.fixture(scope="session")
def notebook_dir() -> Path:
    return Path(panpdf.__file__).parent.parent.parent / "tests/notebooks"


@pytest.fixture(scope="session")
def store(notebook_dir):
    from panpdf.jupyter.stores import Store

    return Store([notebook_dir])


@pytest.fixture(scope="session")
def image_factory():
    def image_factory(id_, url="", caption="caption") -> Image:
        text = f"![{caption}]({url}){{#{id_}}}"
        elems = pf.convert_text(text)
        assert isinstance(elems, list)
        return elems[0].content[0]

    return image_factory
