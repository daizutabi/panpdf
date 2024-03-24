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


@pytest.mark.parametrize("text", ["abcあα", b"abc"])
def test_create_temp_file(text):
    from panpdf.tools import create_temp_file

    with tempfile.TemporaryDirectory() as tmpdir:
        path = create_temp_file(text, suffix=".txt", dir=tmpdir)
        assert path.exists()
        assert path.suffix == ".txt"
        if isinstance(text, str):
            assert path.read_text(encoding="utf8") == text
        else:
            assert path.read_bytes() == text


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


@pytest.mark.parametrize(
    ("text", "color"), [("Error", "red bold"), ("Warning", "red"), ("INFO", "yellow")]
)
def test_get_color(text: str, color):
    from panpdf.tools import get_color

    assert get_color(text) == color
    assert get_color(text.upper()) == color
