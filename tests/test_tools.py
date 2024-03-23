import asyncio
from pathlib import Path

import panflute as pf
import pytest
from panflute import Doc


def test_get_metadata():
    from panpdf.tools import get_metadata

    text = "---\na: a\nb: \\b\n---\n# x"
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    assert get_metadata(doc, "a") == "a"
    assert get_metadata(doc, "b") == "\\b"
    assert get_metadata(doc, "c", "c") == "c"


def test_add_metadata():
    from panpdf.tools import add_metadata, get_metadata

    text = "---\na: a\nb: \\b\n---\n# x"
    doc = pf.convert_text(text, standalone=True)
    assert isinstance(doc, Doc)
    add_metadata(doc, "a", "A")
    assert get_metadata(doc, "a") == "a\nA"
    add_metadata(doc, "c", "C")
    assert get_metadata(doc, "c") == "C"


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


def test_get_file_path():
    from panpdf.tools import get_file_path

    assert get_file_path(None, "") is None
    path = Path(__file__)
    assert get_file_path(path, "") is path


# def test_get_file_data_dir():
#     from panpdf.tools import get_data_dir, get_defaults_file_path

#     data_dir = get_data_dir()
#     with tempfile.mkdtemp(dir=data_dir) as fd:
#         pass


def test_run():
    from panpdf.tools import run

    args = ["python", "-c" "print(1);1/0"]

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

    args = ["python", "-c" "print(1);1/0"]

    assert progress(args)

    args = ["python", "--version"]

    assert not progress(args)
