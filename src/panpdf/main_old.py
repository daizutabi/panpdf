import os
import sys
from pathlib import Path

import click
import nbformat
import panflute as pf
from panflute.tools import pandoc_version

from panpdf import utils
from panpdf.__about__ import __version__
from panpdf.core import config
from panpdf.core.converter import Converter
from panpdf.jupyter.stores import get_ids

pkg_dir = os.path.dirname(os.path.abspath(__file__))


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("-t", "--to", type=str, metavar="FORMAT")
@click.option("-o", "--output", type=str, metavar="FILE")
@click.option("-s", "--standalone", is_flag=True)
@click.option("-e", "--external", is_flag=True, help="Create images externally.")
@click.option("-E", "--external-only", is_flag=True, help="Create images and exit.")
@click.option("-c", "-C", "--citeproc", is_flag=True)
@click.option(
    "-j",
    "--notebook-dir",
    type=str,
    metavar="DIRECTORY",
    default="../notebooks",
    show_default=True,
)
@click.option("-O", "--options", type=str, help="Pandoc options.")
@click.option("-d", "--dry-run", is_flag=True)
@click.option("-D", "--print-defaults", is_flag=True)
@click.option("-H", "--print-include-in-header", is_flag=True)
@click.option("-B", "--print-include-before-body", is_flag=True)
@click.option("-A", "--print-include-after-body", is_flag=True)
@click.option("--list", "list_", is_flag=True, help="List document files.")
@click.option("-v", "--version", is_flag=True)
def cli(
    files: list[str],
    to: str | None,
    output: str | None,
    standalone: bool,
    external: bool,
    external_only: bool,
    citeproc: bool,
    notebook_dir: str,
    options: str | None,
    dry_run: bool,
    list_: bool,
    print_defaults: bool,
    print_include_in_header: bool,
    print_include_before_body: bool,
    print_include_after_body: bool,
    version: bool,
):
    if version:
        click.echo(f"panpdf: {__version__}")
        _pandoc_version = ".".join(str(x) for x in pandoc_version.version)
        click.echo(f"pandoc: {_pandoc_version}")
        click.echo(f"panflute: {pf.__version__}")
        sys.exit()

    if print_defaults:
        click.echo(config.read_source("defaults.yaml"))
        sys.exit()

    if print_include_in_header:
        click.echo(config.read_source("include-in-header.tex"))
        sys.exit()

    if print_include_before_body:
        click.echo(config.read_source("include-before-body.tex"))
        sys.exit()

    if print_include_after_body:
        click.echo(config.read_source("include-after-body.tex"))
        sys.exit()

    if not files and list_:
        files = ["."]
    if not to and not list_:
        to = utils.get_format(output or "", "latex")

    # TODO: version check
    assert pandoc_version.version == (2, 19, 2)
    assert pf.__version__ == "2.3.0"

    if not files and to:
        converter = Converter(notebook_dir=notebook_dir)
        text = prompt()
        text = converter.convert_text(text, output_format=to, standalone=standalone)
        click.echo(text)
        sys.exit()

    if len(files) == 1 and os.path.splitext(files[0])[1] == ".ipynb":
        convert_notebook(files[0])
        sys.exit()

    paths = list(utils.collect(Path(f) for f in files))
    if list_:
        for path in paths:
            click.secho(str(path), bold=True)
        sys.exit()

    converter = Converter(citeproc, notebook_dir, external or external_only)
    extra_args = []

    if options:
        extra_args += options.split(" ")

    text = converter.convert(
        paths,
        output_format=to,
        output=output,
        extra_args=extra_args,
        show_spinner=True,
        external_only=external_only,
        dry_run=dry_run,
    )
    if not output:
        click.echo(text)


def convert_notebook(path: str):
    nb = nbformat.read(path, as_version=4)
    ids = get_ids(nb, "fig")
    notebook_dir, path = os.path.split(path)
    if not notebook_dir:
        notebook_dir = "."
    imgs = [f"![a]({path}){{#{id_}}}\n\n" for id_ in ids]
    text = "".join(imgs)
    converter = Converter(False, notebook_dir, True)
    converter.convert_text(text, standalone=True, external_only=True)


def prompt():
    click.echo("Enter double blank lines to exit.")
    lines: list[str] = []
    while True:
        line = click.prompt("", type=str, default="", show_default=False)
        if lines and lines[-1] == "" and line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip() + "\n"
