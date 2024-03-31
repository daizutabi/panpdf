import sys
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from panpdf.main import cli

runner = CliRunner()
app = typer.Typer()
app.command()(cli)


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    for name in ["pandoc", "panflute", "panpdf"]:
        assert f"{name} " in result.stdout


def test_get_text():
    from panpdf.main import get_text

    files = [Path("examples/src/1.md"), Path("examples/src/2.md")]
    text = get_text(files)
    assert text.startswith("---\n")
    assert "# Section 2" in text


def test_collect():
    from panpdf.main import get_text

    files = [Path("examples/src")]
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
    result = runner.invoke(app, [], input="\n\n")
    assert result.stdout.endswith("No input text. Aborted.\n")


def test_standalone():
    result = runner.invoke(app, ["-s"], input="# section\n")
    assert "\\documentclass[\n]{article}" in result.stdout
    assert "\\begin{document}" in result.stdout


def test_defaults():
    result = runner.invoke(app, ["-d", "examples/defaults"], input="# section\n")
    assert "{jlreq}" in result.stdout
    assert "\\begin{document}" in result.stdout


def test_output_title():
    text = "---\ntitle: Title\n---\n"
    runner.invoke(app, ["-o", ".tex"], input=text)
    path = Path("Title.tex")
    assert path.exists()
    path.unlink()


def test_figure(fmt: str):
    text = f"![a]({fmt}.ipynb){{#fig:{fmt}}}"
    result = runner.invoke(app, ["-n", "notebooks"], input=text)

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
        result = runner.invoke(app, ["-C", "-d", "examples/defaults"], input="[@panflute]")
        assert "\\citeproc{ref-panflute}{{[}1{]}}" in result.stdout


def test_citeproc_not_found():
    result = runner.invoke(app, ["-C"], input="[@x]")
    assert "[WARNING] Citeproc: citation x not found" in result.stdout


def test_figure_only():
    result = runner.invoke(app, ["-F", "-n", "notebooks"], input="abc\n")
    assert result.exit_code == 0
    result.stdout.endswith(": abc\n:\n.\n")


def test_extra_args():
    url = "https://www.zotero.org/styles/ieee"
    text = "[@panflute]"
    argv = sys.argv[:]
    sys.argv.extend(["--", "--csl", url])
    result = runner.invoke(app, ["-C"], input=text)
    assert result.exit_code == 0
    assert "{[}1{]}" in result.stdout
    sys.argv = argv


def test_header():
    text = "---\nrhead: \\includegraphics[width=1cm]{header.pdf}\n---\nabc\n"
    result = runner.invoke(app, ["-d", "examples/defaults"], input=text)
    assert "\\rhead{\\includegraphics[width=1cm]{examples/images/header.pdf}}" in result.stdout
    assert "\\usepackage{graphicx}" in result.stdout


@pytest.mark.parametrize("quiet", [True, False])
def test_quiet(quiet):
    text = "---\ntitle: Title\n---\n"
    args = ["-o", ".pdf"]
    if quiet:
        args.append("--quiet")

    runner.invoke(app, args, input=text)
    path = Path("Title.pdf")
    assert path.exists()
    path.unlink()
