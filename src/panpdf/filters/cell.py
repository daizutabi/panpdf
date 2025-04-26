from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import nbstore.notebook
import panflute as pf
from panflute import CodeBlock, Doc, Element, Figure, Image, Plain

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from nbstore import Store


@dataclass(repr=False)
class Cell(Filter):
    types: ClassVar[type[Figure]] = Figure
    store: Store

    def action(self, figure: Figure, doc: Doc) -> Figure | list[Element]:  # noqa: C901, PLR0911
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

        if url and identifier == ".":
            self.store.url = url
            return figure

        code_block = None
        if "source" in image.classes or "cell" in image.classes:
            code_block = self.get_code_block(url, identifier)

            if "source" in image.classes:
                return [code_block]

            if identifier.startswith("fig:"):
                return [code_block, figure]

        if "output" in image.classes or "cell" in image.classes:
            html = "html" in image.classes
            output = self.get_output(url, identifier, html=html)

            if code_block and output:
                return [code_block, *output]

            if code_block:
                return [code_block]

            if output:
                return output

            return []

        return figure

    def get_code_block(self, url: str, identifier: str) -> CodeBlock:
        try:
            nb = self.store.read(url)
            source = nbstore.notebook.get_source(nb, identifier)
        except ValueError:
            msg = f"[panpdf] Unknown url or id: url='{url}' id='{identifier}'"
            raise ValueError(msg) from None

        lang = nbstore.notebook.get_language(nb)
        return CodeBlock(source.strip(), classes=[lang])

    def get_output(
        self,
        url: str,
        identifier: str,
        *,
        html: bool = False,
    ) -> list[Element] | None:
        try:
            nb = self.store.read(url)
            data = nbstore.notebook.get_data(nb, identifier)
        except ValueError:
            return None

        if "text/html" in data and html:
            text = data["text/html"]
            return pf.convert_text(text, input_format="html")  # type: ignore

        if "text/plain" in data:
            text = data["text/plain"]
            text = text.replace("┆", "│")
            return [CodeBlock(text.rstrip(), classes=["output"])]

        return None
