import asyncio
import atexit
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import panflute as pf
import pytest
from panflute import Doc, Para, Str


def test_get_pandoc_path():
    from panpdf.tools import PANDOC_PATH, get_pandoc_path

    PANDOC_PATH.clear()
    path = get_pandoc_path()
    assert path
    assert PANDOC_PATH[0] is path
    assert get_pandoc_path() == path


def test_get_pandoc_path_invalid():
    from panpdf.tools import PANDOC_PATH, get_pandoc_path

    PANDOC_PATH.clear()
    with pytest.raises(OSError, match="Path"):
        get_pandoc_path("x")


def test_get_pandoc_version():
    from panpdf.tools import get_pandoc_version

    assert get_pandoc_version().startswith("3.")


def test_get_data_dir():
    from panpdf.tools import get_data_dir

    assert get_data_dir().name == "pandoc"


@pytest.mark.parametrize("text", ["abcあα", b"abc"])
def test_create_temp_file(text, tmp_path):
    from panpdf.tools import create_temp_file

    path = create_temp_file(text, suffix=".txt", dir=tmp_path)
    assert path.exists()
    assert path.suffix == ".txt"
    if isinstance(text, str):
        assert path.read_text(encoding="utf8") == text
    else:
        assert path.read_bytes() == text


def test_create_temp_dir(tmp_path):
    from panpdf.tools import create_temp_dir

    path = create_temp_dir(dir=tmp_path)
    assert path.exists()
    assert path.parent == tmp_path


def test_get_file_path():
    from panpdf.tools import get_file_path

    assert get_file_path(None, "") is None
    path = Path(__file__)
    assert get_file_path(path, "") == path
    assert get_file_path(__file__, "") == path


def mock_get_data_dir():
    tmpdir = Path(tempfile.mkdtemp())
    os.mkdir(tmpdir / "defaults")

    atexit.register(lambda: shutil.rmtree(tmpdir))
    return lambda: tmpdir


@pytest.mark.parametrize("suffix", [None, ".yaml"])
@patch("panpdf.tools.get_data_dir", mock_get_data_dir())
def test_get_file_data_dir(suffix):
    from panpdf.tools import create_temp_file, get_data_dir, get_file_path

    dirname = "defaults"
    dir_ = get_data_dir() / dirname
    text = str(uuid.uuid4())
    path = create_temp_file(text, suffix=suffix, dir=dir_)
    path = get_file_path(str(path).replace(path.suffix, ""), "")
    assert path
    assert path.read_text(encoding="utf8") == text
    file = path.name.replace(path.suffix, "")
    path = get_file_path(file, dirname)
    assert path
    assert path.read_text(encoding="utf8") == text


@patch("panpdf.tools.get_data_dir", mock_get_data_dir())
def test_get_gedfaults_file_data_dir_none():
    from panpdf.tools import get_defaults_file_path

    assert get_defaults_file_path(Path("-")) is None


def test_run():
    from panpdf.tools import run

    args = ["python", "-cprint(1);1/0"]

    out: list[str] = []
    err: list[str] = []

    def stdout(output: str) -> None:
        out.append(output)

    def stderr(output: str) -> None:
        err.append(output)

    asyncio.run(run(args, stdout, stderr))
    assert out[0].strip() == "1"
    assert err[0].strip().startswith("Traceback")


def test_progress():
    from panpdf.tools import progress

    args = ["python", "-cprint(1);1/0"]

    assert progress(args)

    args = ["python", "--version"]

    assert not progress(args)


@pytest.mark.parametrize(
    ("text", "color"),
    [("Error", "red"), ("Warning", "yellow"), ("INFO", "gray50")],
)
def test_get_color(text: str, color):
    from panpdf.tools import get_color

    assert get_color(text) == color
    assert get_color(text.upper()) == color


def test_get_metadata_str():
    from panpdf.tools import get_metadata_str

    text = "---\na: a\nb: \\b\n---\n# x"
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    assert get_metadata_str(doc, "a") == "a"
    assert get_metadata_str(doc, "b") == "\\b"
    assert get_metadata_str(doc, "c", "c") == "c"


def test_add_metadata_str():
    from panpdf.tools import add_metadata_str, get_metadata_str

    text = "---\na: a\nb: \\b\n---\n# x"
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    add_metadata_str(doc, "a", "A")
    assert get_metadata_str(doc, "a") == "a\nA"
    add_metadata_str(doc, "c", "C")
    assert get_metadata_str(doc, "c") == "C"


def test_get_metadata_list():
    from panpdf.tools import iter_metadata_list

    doc = Doc()
    doc.metadata["a"] = ["b", "c"]
    assert list(iter_metadata_list(doc, "a")) == ["b", "c"]


def test_add_metadata_list():
    from panpdf.tools import add_metadata_list, iter_metadata_list

    doc = Doc()
    add_metadata_list(doc, "a", "x")
    add_metadata_list(doc, "a", "y")
    assert list(iter_metadata_list(doc, "a")) == ["x", "y"]


def test_convert_metadata():
    doc = Doc()
    doc.metadata["a"] = ["b", "c"]
    m = pf.convert_text(
        doc,
        input_format="panflute",
        output_format="markdown",
        standalone=True,
    )
    assert m == "---\na:\n- b\n- c\n---\n"
    x = doc.metadata["a"]
    assert isinstance(x, pf.MetaList)
    x.append("d")
    assert len(x) == 3


def test_iter_extra_args_from_metadata():
    from panpdf.tools import (
        add_metadata_list,
        create_temp_file,
        iter_extra_args_from_metadata,
    )

    a = create_temp_file("AAA", suffix=".tex").as_posix()
    b = create_temp_file("BBB", suffix=".tex").as_posix()

    doc = Doc(Para(Str("123")))
    add_metadata_list(doc, "include-in-header", a)
    add_metadata_list(doc, "include-in-header", b)
    add_metadata_list(doc, "include-before-body", a)
    add_metadata_list(doc, "include-before-body", b)
    add_metadata_list(doc, "include-after-body", a)
    add_metadata_list(doc, "include-after-body", b)

    extra_args = list(iter_extra_args_from_metadata(doc))

    t = pf.convert_text(
        doc,
        input_format="panflute",
        output_format="latex",
        standalone=True,
        extra_args=extra_args,
    )
    assert isinstance(t, str)
    assert "AAA\nBBB\n" in t
    assert "AAA\n\nBBB\n\n123\n\nAAA\n\nBBB" in t


def test_get_defaults():
    from panpdf.tools import get_defaults

    path = "tests/examples/defaults"
    x = get_defaults(path, "pdf-engine")
    assert x == "lualatex"
    x = get_defaults(path, "resource-path")
    assert x == [".", "tests/examples/images"]


def test_get_defaults_dict():
    from panpdf.tools import get_defaults

    path = "tests/examples/defaults"
    x = get_defaults(path, "variables")
    assert isinstance(x, dict)


def test_get_defaults_none():
    from panpdf.tools import get_defaults

    assert not get_defaults("", "")

    assert not get_defaults("", "")


def test_search_path():
    from panpdf.tools import search_path

    assert search_path("pyproject.toml") == Path("pyproject.toml")

    defaults = "tests/examples/defaults"

    path = search_path("header.pdf", ["tests/examples/images"])
    assert path == Path("tests/examples/images/header.pdf")

    path = search_path("header.png", ["tests/examples/images"])
    assert path == Path("header.png")

    path = search_path("header.pdf", defaults=defaults)
    assert path == Path("tests/examples/images/header.pdf")

    path = search_path("header.png", defaults=defaults)
    assert path == Path("header.png")


def test_resolve_image():
    from panpdf.tools import resolve_image

    defaults = "tests/examples/defaults"

    text = "\\includegraphics[width=1cm]{header.pdf}"
    text = resolve_image(text, defaults=defaults)
    assert text == r"\includegraphics[width=1cm]{tests/examples/images/header.pdf}"


def test_convert_header():
    from panpdf.tools import convert_header

    text = "---\nrhead: \\RIGHT\n---\n# section"
    doc = pf.convert_text(text, output_format="panflute", standalone=True)
    assert isinstance(doc, Doc)
    assert "rhead" in doc.metadata

    convert_header(doc)
    assert "rhead" not in doc.metadata
    assert "include-in-header" in doc.metadata
    p = pf.stringify(doc.metadata["include-in-header"][0])  # type:ignore

    assert "\\usepackage{fancyhdr}" in Path(p).read_text()
    assert "\\rhead{\\RIGHT}" in Path(p).read_text()
