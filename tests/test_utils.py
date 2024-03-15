from pathlib import Path

import pytest

from panpdf import utils


def test_join_files(tmpdir):
    directory = Path(tmpdir)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("# a\n\n1\n")
    b.write_text("# b\n\n2\n")
    text = utils.join_files([a, b])
    assert text == "# a\n\n1\n\n\n# b\n\n2\n"


def test_collect():
    path = Path(utils.__file__).parent.parent
    paths = list(utils.collect(Path(utils.__file__), ".py"))
    assert len(paths) == 1
    paths = list(utils.collect([path], ".py"))
    assert len(paths) > 10


@pytest.mark.parametrize(
    ("path", "fmt"),
    [
        ("a.tex", "latex"),
        ("a.pdf", "pdf"),
    ],
)
def test_get_format(path, fmt):
    assert utils.get_format(path) == fmt


def test_get_format_unknown():
    with pytest.raises(ValueError):  # noqa: PT011
        utils.get_format("")
