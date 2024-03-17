from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import panflute as pf
import typer
from panflute import Doc
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from typer import Argument, Option

from panpdf import utils
from panpdf.__about__ import __version__
from panpdf.converters import action, create_filters


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
    notebooks_dir: Annotated[
        Path,
        Option(
            metavar="DIRECTORY",
            help="Specify the the notebooks directory to search for figures.",
        ),
    ] = Path("../notebooks"),
    defaults: Annotated[
        Path,
        Option(
            "--defaults",
            "-d",
            metavar="FILE",
            help="Specify a set of default option settings.",
        ),
    ] = Path("defaults.yaml"),
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
        ),
    ] = None,
    version: Annotated[
        bool,
        Option(
            "--version",
            "-v",
            help="Show version and exit.",
        ),
    ] = False,
):
    if version:
        show_version(pandoc_path)

    if not files:
        text = prompt()

    else:
        files = list(utils.collect(file for file in files))
        text = utils.join_files(files)

    if not text:
        typer.secho("No input text. Aborted.", fg="red")
        raise typer.Exit

    extra_args = []

    if defaults.exists():
        extra_args.extend(["--defaults", defaults.as_posix()])

    doc: Doc = pf.convert_text(
        text,
        standalone=True,
        pandoc_path=pandoc_path,
        extra_args=extra_args,
    )  # type:ignore

    if output and str(output).startswith("."):
        title = utils.get_metadata(doc, "title") or "a"
        output = Path(f"{title}{output}")

    if output_format == OutputFormat.auto:
        if not output or output.suffix == ".tex":
            output_format = OutputFormat.latex
        elif output.suffix == ".pdf":
            output_format = OutputFormat.pdf
        else:
            typer.secho(f"Unknown output format: {output.suffix}", fg="red")
            raise typer.Exit

    if output_format == OutputFormat.pdf:
        standalone = True

    filters = create_filters(notebooks_dir, standalone=standalone_figure, citeproc=citeproc)
    doc = action(doc, filters, figure_only=figure_only)

    if citeproc:
        extra_args.append("--citeproc")

    if output:
        extra_args.extend(["--output", output.as_posix()])

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=False,
    ) as progress:
        progress.add_task(f'[green]Producing "{output}"', total=None)

        tex = pf.convert_text(
            doc,
            input_format="panflute",
            output_format=output_format.value,
            standalone=standalone,
            extra_args=extra_args,
        )

    if not output:
        typer.echo(tex)

    # text = utils.join_files(files)
    # typer.echo(text)

    # typer.echo(files)
    # typer.echo(output_dir)
    # typer.echo(data_dir)
    # typer.echo(notebooks_dir)

    # if output_format == "pdf":
    #     standalone = True

    # if paths:
    #     text = utils.join_files(paths)
    # elif not text:
    #     return None


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
    output: str = pf.run_pandoc(args=["--version"], pandoc_path=pandoc_path)
    pandoc_version = output.splitlines()[0].split(" ")[1]

    typer.echo(f"pandoc {pandoc_version}")
    typer.echo(f"panflute {pf.__version__}")
    typer.echo(f"panpdf {__version__}")
    raise typer.Exit


def main():
    typer.run(cli)


if __name__ == "__main__":
    main()
