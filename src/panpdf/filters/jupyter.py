from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from panflute import CodeBlock, Image, Para

from panpdf.filters.filter import Filter
from panpdf.jupyter.converters import convert
from panpdf.jupyter.stores import Store

if TYPE_CHECKING:
    from collections.abc import Iterator

    from panflute import Doc, Element


@dataclass
class Jupyter(Filter):
    types: tuple[type[Element], ...] = (Para,)
    store: Store = field(default_factory=Store)

    def action(self, elem: Para, doc: Doc) -> list[Para | CodeBlock]:  # noqa: ARG002
        return list(image_scanner(self.store, elem))


def image_scanner(store: Store, para: Para) -> Iterator[Para | CodeBlock]:
    collected: list[Element] = []

    for elem in para.content:
        if isinstance(elem, Image):
            image = convert_from_store(store, elem)

            if isinstance(image, CodeBlock):
                if collected:
                    yield Para(*collected)
                    collected = []

                yield image
                continue

        collected.append(elem)

    if collected:
        yield Para(*collected)


def convert_from_store(store: Store, elem: Image) -> Image | CodeBlock:
    url = elem.url
    id_ = elem.identifier
    if id_ and (not url or url.endswith(".ipynb")):
        if isinstance(elem, Image) and "source" in elem.classes:
            data = store.get_source(id_, url)
        else:
            try:
                data = store.get_data(id_, url)
            except ValueError:
                # TODO: log
                print(f"[panpdf] Unknown url or id: url='{url}' id='{id_}'")
                sys.exit(1)

        if data:
            return convert(data, elem, language=store.get_language())

    return elem
