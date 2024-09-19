from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from panflute import CodeBlock, Doc, Element, Figure, Image, Plain

from panpdf.filters.filter import Filter
from panpdf.stores import Store


@dataclass(repr=False)
class Cell(Filter):
    types: ClassVar[type[Figure]] = Figure
    store: Store = field(default_factory=Store)

    def action(self, figure: Figure, doc: Doc) -> Figure | list[Element]:
        if not figure.content:
            return figure

        plain = figure.content[0]

        if not isinstance(plain, Plain):
            return figure

        image = plain.content[0]
        if not isinstance(image, Image):
            return figure

        url = image.url
        identifier = image.identifier or figure.identifier

        if not identifier or (url and not url.endswith(".ipynb")):
            return figure

        if "source" in image.classes or "cell" in image.classes:
            code_block = self.get_code_block(url, identifier)

            if "source" in image.classes:
                return [code_block]

            return [code_block, figure]

        return figure

    def get_code_block(self, url: str, identifier: str) -> CodeBlock:
        try:
            source = self.store.get_source(url, identifier)
        except ValueError:
            msg = f"[panpdf] Unknown url or id: url='{url}' id='{identifier}'"
            raise ValueError(msg) from None

        lang = self.store.get_language(url)
        return CodeBlock(source.strip(), classes=[lang])
