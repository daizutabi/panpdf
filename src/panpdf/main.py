import os
import sys
from collections.abc import Iterable, Iterator
from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import panflute as pf
import typer
from panflute import Doc
from typer import Argument, Option

if TYPE_CHECKING:
    from panpdf.filters.filter import Filter

EXTRA_ARGS: list[str] = []

if "--" in sys.argv:
    index = sys.argv.index("--")
    EXTRA_ARGS[:] = sys.argv[index + 1 :]
    sys.argv = sys.argv[:index]


class OutputFormat(str, Enum):
    latex = "latex"
    pdf = "pdf"
    auto = "auto"


app = typer.Typer(add_completion=False)


@app.command(name="panpdf")
def cli(  # noqa: C901, PLR0912, PLR0913
    files: Annotated[
        list[Path] | None,
        Argument(
            help="Input files or directories.",
            show_default=False,
        ),
    ] = None,
    *,
    output_format: Annotated[
        OutputFormat,
        Option("--to", "-t", help="Output format.", show_default="auto"),  # type: ignore
    ] = OutputFormat.auto,
    output: Annotated[
        Path | None,
        Option(
            "--output",
            "-o",
            metavar="FILE",
            help="Write output to FILE instead of stdout.",
            show_default=False,
        ),
    ] = None,
    data_dir: Annotated[  # noqa: ARG001
        Path | None,
        Option(
            metavar="DIRECTORY",
            help="Specify the user data directory to search for pandoc data files.",
            hidden=True,
        ),
    ] = None,
    notebooks_dir: Annotated[
        Path | None,
        Option(
            "--notebooks-dir",
            "-n",
            metavar="DIRECTORY",
            help="Specify the notebooks directory to search for figures.",
            show_default=False,
        ),
    ] = None,
    defaults: Annotated[
        Path | None,
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
        ),
    ] = False,
    standalone_figure: Annotated[
        bool,
        Option(
            "--standalone-figure",
            "-f",
            help="Produce output with standalone figures.",
        ),
    ] = False,
    figure_only: Annotated[
        bool,
        Option(
            "--figure-only",
            "-F",
            help="Produce standalone figures and exit.",
            hidden=True,
        ),
    ] = False,
    citeproc: Annotated[
        bool,
        Option(
            "--citeproc",
            "-C",
            help="Process the citations in the file.",
        ),
    ] = False,
    pandoc_path: Annotated[
        Path | None,
        Option(
            metavar="FILE",
            help="If specified, use the Pandoc at this path.",
            show_default=False,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        Option(
            "--verbose",
            help="Give verbose debugging output.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        Option("--quiet", help="Suppress warning messages."),
    ] = False,
    version: Annotated[
        bool,
        Option(
            "--version",
            "-v",
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    """Optionally, you can add extra pandoc options after --.

    Example usage: panpdf -o dest.pdf src.md -- --pdf-engine lualatex
    """
    if version:
        show_version(pandoc_path)

    from nbstore import Store

    from panpdf.filters.attribute import Attribute
    from panpdf.filters.cell import Cell
    from panpdf.filters.crossref import Crossref
    from panpdf.filters.jupyter import Jupyter
    from panpdf.filters.layout import Layout
    from panpdf.filters.snippet import Snippet
    from panpdf.filters.verbatim import Verbatim
    from panpdf.filters.zotero import Zotero
    from panpdf.tools import (
        convert_doc,
        get_defaults_file_path,
        get_metadata_str,
        iter_extra_args_from_metadata,
    )

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

    filters: list[Filter] = [Attribute(), Snippet()]

    if notebooks_dir:
        store = Store(notebooks_dir.absolute())
        cell = Cell(store)
        jupyter = Jupyter(store, defaults_path, standalone_figure, pandoc_path)
        filters.extend([cell, jupyter])

    filters.extend([Verbatim(), Layout(), Crossref()])

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

    if EXTRA_ARGS:
        extra_args.extend(EXTRA_ARGS)

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

    if text := sys.stdin.read():
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


def show_version(pandoc_path: Path | None) -> None:
    from panpdf.tools import get_pandoc_version

    pandoc_version = get_pandoc_version(pandoc_path)

    typer.echo(f"pandoc {pandoc_version}")
    typer.echo(f"panflute {pf.__version__}")
    typer.echo(f"panpdf {version('panpdf')}")
    raise typer.Exit
