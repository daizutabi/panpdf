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


# @pytest.fixture(scope="session")
# def nb(root):
#     return nbformat.read(root / "tests/test.ipynb", as_version=4)


# @pytest.fixture(scope="session")
# def store(root):
#     store = Store(path=[root])
#     store.get_notebook("tests/test.ipynb")
#     return store


# def get_doc(text):
#     text = inspect.cleandoc(text)
#     return pf.convert_text(text, standalone=True)


# @pytest.fixture(scope="module")
# def doc():
#     text = """# section

#     abc

#     `a = 1`

#     ``` {#block .python .qt a=1}
#     a = 1
#     ```
#     """

#     return get_doc(text)


# @pytest.fixture
# def docdir(tmpdir):
#     text = "# section\n\nテキスト\n"
#     for name in ["a", "b"]:
#         path = Path(tmpdir.join(f"{name}.md"))
#         path.write_text(text, encoding="utf8")
#     subdir = tmpdir.mkdir("c")
#     for name in ["d", "e"]:
#         path = Path(subdir.join(f"{name}.md"))
#         path.write_text(text, encoding="utf8")
#     return Path(tmpdir)


# @pytest.fixture(scope="session")
# def math_factory():
#     attributes = Attributes()

#     def math_factory(id, url="."):  # noqa: A002
#         text = f"$${url}$$ {{#{id}}}"
#         doc = attributes.run(text)
#         return doc.content[0].content[0].content[0]  # type:ignore

#     return math_factory


# @pytest.fixture(scope="session")
# def runner(nb):
#     runner = CliRunner()
#     with runner.isolated_filesystem():
#         Path("a.md").write_text("a\nb\nc\n")
#         Path("b.md").write_text("d\ne\nf\n")
#         text = "---\ntitle: internal\nsecurity: internal\n"
#         text += "logo: blue\nheaderrulewidth: 1.0pt\n---\n"
#         Path("internal.md").write_text(text)
#         nbformat.write(nb, "test.ipynb")
#         yield runner


# @pytest.fixture(scope="session")
# def converter(root):
#     converter = Converter()
#     store: Store = converter.filters["jupyter"].store  # type: ignore
#     store.path = [root]
#     return converter


# @pytest.fixture(scope="session")
# def convert_text(converter):
#     return converter.convert_text


# @pytest.fixture(scope="session")
# def convert(converter):
#     return converter.convert
