import os
import sys
from collections.abc import Iterable, Iterator
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import panflute as pf
import typer
from panflute import Doc
from typer import Argument, Option

from panpdf.__about__ import __version__
from panpdf.filters.attribute import Attribute
from panpdf.filters.crossref import Crossref
from panpdf.filters.jupyter import Jupyter
from panpdf.filters.layout import Layout
from panpdf.filters.verbatim import Verbatim
from panpdf.filters.zotero import Zotero
from panpdf.stores import Store
from panpdf.tools import (
    convert_doc,
    get_defaults_file_path,
    get_metadata_str,
    get_pandoc_version,
    iter_extra_args_from_metadata,
)

if TYPE_CHECKING:
    from panpdf.filters.filter import Filter


class OutputFormat(str, Enum):
    latex = "latex"
    pdf = "pdf"
    auto = "auto"


def cli(
    files: Annotated[
        Optional[list[Path]],
        Argument(
            help="Input files or directories.",
            show_default=False,
        ),
    ] = None,
    *,
    output_format: Annotated[
        OutputFormat, Option("--to", "-t", help="Output format.", show_default="auto")  # type: ignore
    ] = OutputFormat.auto,
    output: Annotated[
        Optional[Path],
        Option(
            "--output",
            "-o",
            metavar="FILE",
            help="Write output to FILE instead of stdout.",
            show_default=False,
        ),
    ] = None,
    data_dir: Annotated[
        Optional[Path],
        Option(
            metavar="DIRECTORY",
            help="Specify the user data directory to search for pandoc data files.",
            hidden=True,
        ),
    ] = None,
    notebooks_dir: Annotated[
        Optional[Path],
        Option(
            "--notebooks-dir",
            "-n",
            metavar="DIRECTORY",
            help="Specify the notebooks directory to search for figures.",
            show_default=False,
        ),
    ] = None,
    defaults: Annotated[
        Optional[Path],
        Option(
            "--defaults",
            "-d",
            metavar="FILE",
            help="Specify a set of default option settings.",
            show_default=False,
        ),
    ] = None,
    standalone: Annotated[
        bool,
        Option(
            "--standalone",
            "-s",
            help="Produce output with an appropriate header and footer.",
            is_flag=True,
        ),
    ] = False,
    standalone_figure: Annotated[
        bool,
        Option(
            "--standalone-figure",
            "-f",
            help="Produce output with standalone figures.",
            is_flag=True,
        ),
    ] = False,
    figure_only: Annotated[
        bool,
        Option(
            "--figure-only",
            "-F",
            help="Produce standalone figures and exit.",
            is_flag=True,
            hidden=True,
        ),
    ] = False,
    citeproc: Annotated[
        bool,
        Option(
            "--citeproc",
            "-C",
            help="Process the citations in the file.",
            is_flag=True,
        ),
    ] = False,
    pandoc_path: Annotated[
        Optional[Path],
        Option(
            metavar="FILE",
            help="If specified, use the Pandoc at this path. If None, default to that from PATH.",
            show_default=False,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        Option(
            "--verbose",
            help="Give verbose debugging output.",
            is_flag=True,
        ),
    ] = False,
    quiet: Annotated[
        bool,
        Option(
            "--quiet",
            help="Suppress warning messages.",
            is_flag=True,
        ),
    ] = False,
    # host: Annotated[
    #     str,
    #     Option(
    #         help="IP address.",
    #         hidden=True,
    #     ),
    # ] = "localhost",
    # port: Annotated[
    #     int,
    #     Option(
    #         help="Port.",
    #         hidden=True,
    #     ),
    # ] = 23119,
    version: Annotated[
        bool,
        Option(
            "--version",
            "-v",
            help="Show version and exit.",
        ),
    ] = False,
):
    """
    Optionally, you can add extra pandoc options after --.

    Example usage: panpdf -o dest.pdf src.md -- --pdf-engine lualatex
    """
    if version:
        show_version(pandoc_path)

    text = get_text(files)

    extra_args = []

    if defaults_path := get_defaults_file_path(defaults):
        extra_args.extend(["--defaults", defaults_path.as_posix()])

    doc: Doc = pf.convert_text(
        text,
        standalone=True,
        extra_args=extra_args[:],
        pandoc_path=pandoc_path,
    )  # type:ignore

    if output and str(output).startswith("."):
        title = get_metadata_str(doc, "title") or "a"
        output = Path(f"{title}{output}")

    if output_format == OutputFormat.auto:
        output_format = get_output_format(output)

    if output_format == OutputFormat.pdf and not output:
        typer.secho("No output file. Aborted.", fg="red")
        raise typer.Exit

    filters: list[Filter] = [Attribute(), Verbatim()]

    if notebooks_dir:
        store = Store([notebooks_dir.absolute()])
        jupyter = Jupyter(defaults_path, standalone_figure, pandoc_path, store)
        filters.append(jupyter)

    filters.extend([Layout(), Crossref()])

    if citeproc:
        filters.append(Zotero())

    for filter_ in filters:
        doc = filter_.run(doc)
        if figure_only and isinstance(filter_, Jupyter):
            raise typer.Exit

    extra_args.extend(iter_extra_args_from_metadata(doc, defaults=defaults))

    if citeproc:
        extra_args.append("--citeproc")

    if output:
        extra_args.extend(["--output", output.as_posix()])

    if "--" in sys.argv:
        extra_args.extend(sys.argv[sys.argv.index("--") + 1 :])

    result = convert_doc(
        doc,
        output_format=output_format.value,
        standalone=standalone,
        extra_args=extra_args,
        pandoc_path=pandoc_path,
        verbose=verbose,
        quiet=quiet,
    )

    if not output and isinstance(result, str):
        typer.echo(result)


def get_text(files: list[Path] | None) -> str:
    if files:
        it = (file.read_text(encoding="utf8") for file in collect(files))
        return "\n\n".join(it)

    if text := prompt():
        return text

    typer.secho("No input text. Aborted.", fg="red")
    raise typer.Exit


def collect(files: Iterable[Path]) -> Iterator[Path]:
    for file in files:
        if file.is_dir():
            for dirpath, dirnames, filenames in os.walk(file):
                dirnames.sort()
                for filename in sorted(filenames):
                    if filename.endswith(".md"):
                        yield Path(dirpath) / filename

        elif file.suffix == ".md":
            yield file


def get_output_format(output: Path | None) -> OutputFormat:
    if not output or output.suffix == ".tex":
        return OutputFormat.latex

    if output.suffix == ".pdf":
        return OutputFormat.pdf

    typer.secho(f"Unknown output format: {output.suffix}", fg="red")
    raise typer.Exit


def prompt() -> str:
    typer.secho("Enter double blank lines to exit.", fg="green")
    lines: list[str] = []

    while True:
        suffix = ": " if not lines or lines[-1] else ". "
        line = typer.prompt("", type=str, default="", prompt_suffix=suffix, show_default=False)
        if lines and lines[-1] == "" and line == "":
            break

        lines.append(line)

    return "\n".join(lines).rstrip()


def show_version(pandoc_path: Path | None):
    pandoc_version = get_pandoc_version()

    typer.echo(f"pandoc {pandoc_version}")
    typer.echo(f"panflute {pf.__version__}")
    typer.echo(f"panpdf {__version__}")
    raise typer.Exit


def main():
    typer.run(cli)  # no cov


if __name__ == "__main__":
    main()  # no cov

# def convert_notebook(path: str):
#     nb = nbformat.read(path, as_version=4)
#     ids = get_ids(nb, "fig")
#     notebook_dir, path = os.path.split(path)
#     if not notebook_dir:
#         notebook_dir = "."
#     imgs = [f"![a]({path}){{#{identifier}}}\n\n" for identifier in ids]
#     text = "".join(imgs)
#     converter = Converter(False, notebook_dir, True)
#     converter.convert_text(text, standalone=True, external_only=True)
