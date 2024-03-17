import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import panflute as pf
from panflute import Doc

from panpdf import utils
from panpdf.config import defaults_option
from panpdf.filters.attribute import Attribute
from panpdf.filters.crossref import Crossref
from panpdf.filters.filter import Filter
from panpdf.filters.jupyter import Jupyter
from panpdf.filters.latex import Latex
from panpdf.filters.layout import Layout
from panpdf.filters.outputcell import OutputCell
from panpdf.filters.zotero import Zotero
from panpdf.stores import Store


def create_filters(
    notebooks_dir: Path | None,
    *,
    standalone: bool = False,
    citeproc: bool = False,
) -> list[Filter]:
    filters = [Attribute(), OutputCell(), Latex()]

    if notebooks_dir:
        jupyter = Jupyter(Store([notebooks_dir.absolute()]))
        filters.append(jupyter)

    filters.extend((Layout(standalone), Crossref()))

    if citeproc:
        filters.append(Zotero())

    return filters


def action(doc: Doc, filters: list[Filter], *, figure_only: bool = False) -> Doc:
    for filter_ in filters:
        doc = filter_.run(doc)
        if figure_only and isinstance(filter_, Layout):
            break

    return doc


@dataclass
class Converter:
    citeproc: bool = False
    notebooks_dir: str | None = None
    external: bool = False
    filters: dict[str, Filter] = field(init=False)

    def __post_init__(self):
        self.filters = {
            "attribute": Attribute(),
            "outputcell": OutputCell(),
            "latex": Latex(),
            "jupyter": Jupyter(),
            "layout": Layout(standalone=self.external),
            "crossref": Crossref(),
        }

        if self.citeproc:
            self.filters["zotero"] = Zotero()

        if self.notebooks_dir:
            jupyter: Jupyter = self.filters["jupyter"]  # type:ignore
            jupyter.store.path = [Path(self.notebooks_dir).absolute()]

    def convert_text(
        self,
        text: str | Doc,
        *,
        input_format: str = "markdown",
        output_format: str = "panflute",
        standalone: bool = False,
        extra_args: list[str] | None = None,
        external_only: bool = False,
    ):
        if isinstance(text, Doc):
            doc = text
        else:
            doc: Doc = pf.convert_text(  # type:ignore
                text,
                input_format=input_format,
                output_format="panflute",
                standalone=True,
            )

        for filter_ in self.filters.values():
            doc = filter_.run(doc)  # type:ignore
            if external_only and isinstance(filter_, Layout):
                sys.exit()  # pragma: no cover

        if output_format == "panflute":
            return doc

        return pf.convert_text(
            doc,
            input_format="panflute",
            output_format=output_format,
            standalone=standalone,
            extra_args=extra_args,
        )

    def convert(
        self,
        paths: Iterable[str] | Iterable[Path] | str | Path | None = None,
        *,
        text: str | Doc | None = None,
        output_format: str | None = None,
        output: Path | str | None = None,
        standalone: bool = False,
        extra_args: Iterable[str] | None = None,
        show_spinner: bool = False,
        external_only: bool = False,
        dry_run: bool = False,
    ):
        if not output_format:
            if output is None:
                output_format = "panflute"
            elif isinstance(output, str) and output.startswith("."):
                output_format = utils.get_format("a" + output)
            else:
                output_format = utils.get_format(output)

        if output_format == "pdf":
            standalone = True

        if paths:
            text = utils.join_files(paths)
        elif not text:
            return None

        doc: Doc = self.convert_text(  # type:ignore
            text,
            standalone=True,
            external_only=external_only,
        )

        if output_format == "panflute" or dry_run:
            return doc

        if isinstance(output, str) and output.startswith("."):
            output = doc.get_metadata().get("title", "a") + output  # type:ignore

        extra_args = [] if extra_args is None else list(extra_args)
        with defaults_option(doc.get_metadata()) as options:  # type:ignore
            extra_args += options
            if output:
                extra_args += ["--output", str(output)]
            if self.citeproc:
                extra_args += ["--citeproc"]
            spinner = None
            if show_spinner and output:
                spinner = halo.Halo(f"Creating {output}")
                spinner.start()
            try:
                text = pf.convert_text(  # type:ignore
                    doc,
                    input_format="panflute",
                    output_format=output_format,
                    standalone=standalone,
                    extra_args=extra_args,
                )
            except (OSError, UnicodeDecodeError):
                if spinner:
                    spinner.fail()
                print("Pandocコマンド実行中にエラー発生。")  # noqa: T201
                raise
            else:
                if spinner:
                    spinner.succeed()

        if not output:
            return text

        return None
