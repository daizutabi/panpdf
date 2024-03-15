from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from panflute import Caption, Doc, Element, Math, Para, Span, Str, Table

from panpdf import utils
from panpdf.core.filter import Filter


@dataclass
class Attributes(Filter):
    types: tuple[type[Element], type[Element]] = (Table, Para)

    def action(self, elem: Table | Para, doc: Doc | None):
        if isinstance(elem, Table):
            plain = elem.caption.content[0]  # type:ignore
            if plain := utils.set_attributes(elem, plain):  # type:ignore
                elem.caption = Caption(plain)
        else:
            return Para(*math_scanner(elem.content))


def math_scanner(elems: Iterable[Element]) -> Iterator[Element]:
    collected: list[Element] = []
    # TODO: caption position
    for elem in elems:
        if isinstance(elem, Math) and elem.format == "DisplayMath":
            yield from collected
            collected = [Span(elem)]
        elif not collected:
            yield elem
        elif isinstance(elem, Str) and elem.text.endswith("}"):
            attrs = Para(*collected[1:], elem)
            utils.set_attributes(collected[0], attrs)
            yield collected[0]
            collected = []
        else:
            collected.append(elem)
    yield from collected
