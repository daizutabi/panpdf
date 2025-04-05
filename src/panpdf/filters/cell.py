from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

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

        code_block = None
        if "source" in image.classes or "cell" in image.classes:
            code_block = self.get_code_block(url, identifier)

            if "source" in image.classes:
                return [code_block]

            if identifier.startswith("fig:"):
                return [code_block, figure]

        if "output" in image.classes or "cell" in image.classes:
            stream = self.store.get_stream(url, identifier)
            html = "html" in image.classes
            output = self.get_output(url, identifier, stream, html=html)

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
            source = self.store.get_source(url, identifier)
        except ValueError:
            msg = f"[panpdf] Unknown url or id: url='{url}' id='{identifier}'"
            raise ValueError(msg) from None

        lang = self.store.get_language(url)
        return CodeBlock(source.strip(), classes=[lang])

    def get_output(
        self,
        url: str,
        identifier: str,
        stream: str | None = None,
        *,
        html: bool = False,
    ) -> list[Element] | None:
        try:
            data = self.store.get_data(url, identifier)
        except ValueError:
            if stream:
                return [CodeBlock(stream.strip(), classes=["output"])]

            return None

        if "text/html" in data and html:
            text = data["text/html"]
            return pf.convert_text(text, input_format="html")  # type: ignore

        if "text/plain" in data:
            text = data["text/plain"]
            text = text.replace("┆", "│")
            if stream:
                text = f"{stream}{text}"

            return [CodeBlock(text, classes=["output"])]

        return None
