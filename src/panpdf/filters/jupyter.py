import sys
from collections.abc import Iterator
from dataclasses import dataclass, field

from panflute import CodeBlock, Doc, Element, Image, Math, Para, Span, Table

from panpdf.core.filter import Filter
from panpdf.jupyter.elements import convert
from panpdf.jupyter.stores import Store


@dataclass
class Jupyter(Filter):
    types: tuple[type[Element], ...] = (Para, Math)
    store: Store = field(default_factory=Store)

    def action(self, elem: Para | Math, doc: Doc):
        if isinstance(elem, Math):
            if (span := elem.parent) and isinstance(span, Span):
                if (url := elem.text) == ".":
                    url = ""
                id_ = span.identifier
                return convert_from_store(self.store, elem, id_, url)
        elif isinstance(elem, Para):
            return list(image_scanner(self.store, elem))


def convert_from_store(
    store: Store,
    elem: Image | Math,
    id_: str,
    url: str,
) -> Image | Math | Table | CodeBlock:
    if id_ and (not url or url.endswith(".ipynb")):
        if isinstance(elem, Image) and "source" in elem.classes:
            data: str | dict = store.get_source(id_, url)
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


def image_scanner(store: Store, para: Para) -> Iterator[Para | CodeBlock | Table]:
    collected: list[Element] = []
    for elem in para.content:
        if isinstance(elem, Image):
            url = elem.url
            id_ = elem.identifier
            elem = convert_from_store(store, elem, id_, url)
            if isinstance(elem, CodeBlock | Table):
                if collected:
                    yield Para(*collected)
                yield elem
                collected = []
                continue
        collected.append(elem)
    if collected:
        yield Para(*collected)
