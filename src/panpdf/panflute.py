from __future__ import annotations

from typing import TYPE_CHECKING

import panflute as pf
from panflute import Doc
from rich.console import Console

if TYPE_CHECKING:
    from pathlib import Path

console = Console()


def get_metadata(doc: Doc, name: str, default: str | None = None) -> str | None:
    if title := doc.metadata.content.get(name):
        return pf.stringify(title)

    return default


def convert_text(
    text,
    *,
    input_format: str = "panflute",
    output_format: str = "latex",
    standalone: bool = False,
    extra_args: list[str] | None = None,
    pandoc_path: Path | None = None,
):
    with console.status("[green]Producing..."):
        return pf.convert_text(
            text,
            input_format=input_format,
            output_format=output_format,
            standalone=standalone,
            extra_args=extra_args,
            pandoc_path=pandoc_path,
        )
