import platform
import subprocess
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from panpdf.main import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    for name in ["pandoc", "panflute", "panpdf"]:
        assert f"{name} " in result.stdout


def test_get_text():
    from panpdf.main import get_text

    files = [Path("tests/examples/src/1.md"), Path("tests/examples/src/2.md")]
    text = get_text(files)
    assert text.startswith("---\n")
    assert "# Section 2" in text


def test_collect():
    from panpdf.main import get_text

    files = [Path("tests/examples/src")]
    text = get_text(files)
    assert text.startswith("---\n")
    assert "# Section 2" in text


@pytest.mark.parametrize("to", [None, "latex", "pdf"])
def test_prompt(to):
    args = ["--to", to] if to else []
    result = runner.invoke(app, args, input="# section\n")
    if to == "pdf":
        assert result.stdout.endswith("No output file. Aborted.\n")
    else:
        assert "\\section{section}\\label{section}" in result.stdout


def test_prompt_empty():
    result = runner.invoke(app, [], input="")
    assert result.stdout.endswith("No input text. Aborted.\n")


def test_standalone():
    result = runner.invoke(app, ["-s"], input="# section\n")
    assert "\\documentclass[\n]{article}" in result.stdout
    assert "\\begin{document}" in result.stdout


def test_defaults():
    result = runner.invoke(app, ["-d", "tests/examples/defaults"], input="# section\n")
    assert "{jlreq}" in result.stdout
    assert "\\begin{document}" in result.stdout


def test_output_title(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    text = "---\ntitle: Title\n---\n"
    runner.invoke(app, ["-o", ".tex"], input=text)
    path = Path("Title.tex")
    assert path.exists()


def test_figure(fmt: str):
    if fmt == "svg" and platform.system() == "Windows":
        return

    text = f"![a]({fmt}.ipynb){{#fig:{fmt}}}"
    result = runner.invoke(app, ["-n", "tests/notebooks"], input=text)

    fmt = fmt.replace("svg", "pdf")
    if fmt == "pgf":
        assert "\\usepackage{pgf}" in result.stdout
        assert "%% Creator: Matplotlib, " in result.stdout
    else:
        assert f".{fmt}}}" in result.stdout


def test_output_format():
    from panpdf.main import OutputFormat, get_output_format

    assert get_output_format(None) is OutputFormat.latex
    assert get_output_format(Path("a.tex")) is OutputFormat.latex
    assert get_output_format(Path("a.pdf")) is OutputFormat.pdf

    with pytest.raises(typer.Exit):
        get_output_format(Path("a.png"))


def test_citeproc():
    result = runner.invoke(app, ["-C"], input="[@panflute]")
    assert "(Correia {[}2016{]} 2024)" in result.stdout
    assert "\\url{https://github.com/sergiocorreia/panflute}." in result.stdout


def test_citeproc_csl():
    from panpdf.tools import get_pandoc_version

    if get_pandoc_version() > "3.1":
        result = runner.invoke(
            app,
            ["-C", "-d", "tests/examples/defaults"],
            input="[@panflute]",
        )
        assert "\\citeproc{ref-panflute}{{[}1{]}}" in result.stdout


def test_citeproc_not_found():
    result = runner.invoke(app, ["-C"], input="[@x]")
    assert "[WARNING] Citeproc: citation x not found" in result.stdout


def test_figure_only():
    result = runner.invoke(app, ["-F", "-n", "tests/notebooks"], input="abc\n")
    assert result.exit_code == 0
    assert not result.stdout


def test_extra_args():
    url = "https://www.zotero.org/styles/ieee"
    text = "[@panflute]\n\n"
    args = ["panpdf", "-C", "--", "--csl", url]
    out = subprocess.check_output(args, input=text, text=True)
    assert "{[}1{]}" in out


def test_header():
    text = "---\nrhead: \\includegraphics[width=1cm]{header.pdf}\n---\nabc\n"
    result = runner.invoke(app, ["-d", "tests/examples/defaults"], input=text)
    assert (
        "\\rhead{\\includegraphics[width=1cm]{tests/examples/images/header.pdf}}"
        in result.stdout
    )
    assert "\\usepackage{graphicx}" in result.stdout


@pytest.mark.parametrize("quiet", [True, False])
def test_quiet(quiet, tmp_path: Path):
    text = "---\ntitle: Title\n---\n"
    args = ["-o", (tmp_path / "a.pdf").as_posix()]
    if quiet:
        args.append("--quiet")

    runner.invoke(app, args, input=text)
    path = tmp_path / "a.pdf"
    assert path.exists()


def test_command(tmp_path: Path):
    out = tmp_path / "a.pdf"

    args = [
        "panpdf",
        "tests/examples/src",
        "-n",
        "tests/notebooks",
        "-d",
        "tests/examples/defaults.yaml",
        "-C",
        "-o",
        out.as_posix(),
    ]
    subprocess.run(args, check=False)
    assert out.exists()

    p = subprocess.run(["pdffonts", out.as_posix()], check=False, capture_output=True)
    stdout = p.stdout.decode("utf-8")

    fonts = ["Pagella", "HaranoAji", "Heros", "DejaVuSansMono", "LMRoman"]
    for font in fonts:
        assert font in stdout
