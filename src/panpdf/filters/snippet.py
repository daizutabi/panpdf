from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from panflute import CodeBlock, Doc, Figure, Image, Plain

from panpdf.filters.filter import Filter


@dataclass(repr=False)
class Snippet(Filter):
    types: ClassVar[type[Figure]] = Figure

    def action(self, figure: Figure, doc: Doc) -> Figure | CodeBlock:
        if not figure.content:
            return figure

        plain = figure.content[0]

        if not isinstance(plain, Plain):
            return figure

        image = plain.content[0]
        if not isinstance(image, Image):
            return figure

        url = image.url
        if not Path(url).is_file():
            return figure

        identifier = image.identifier or figure.identifier

        if identifier or "source" not in image.classes:
            return figure

        text = Path(url).read_text(encoding="utf-8")
        classes = [cls for cls in image.classes if cls != "source"]
        return CodeBlock(text, classes=classes, attributes=image.attributes)  # type: ignore
