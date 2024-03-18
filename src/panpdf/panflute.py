from __future__ import annotations

from pathlib import Path

import panflute as pf
from panflute import Doc
from rich.console import Console

console = Console()


def get_metadata(doc: Doc, name: str, default: str | None = None) -> str | None:
    if title := doc.metadata.content.get(name):
        return pf.stringify(title)

    return default


def convert_text(
    doc: Doc,
    *,
    output_format: str,
    standalone: bool,
    extra_args: list[str] | None = None,
    pandoc_path: Path | None = None,
):
    with console.status("[green]Producing..."):
        return pf.convert_text(
            doc,
            input_format="panflute",
            output_format=output_format,
            standalone=standalone,
            extra_args=extra_args,
            pandoc_path=pandoc_path,
        )
