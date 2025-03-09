from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import panflute as pf
from panflute import (
    Caption,
    Figure,
    Image,
    Math,
    Para,
    Plain,
    SoftBreak,
    Space,
    Span,
    Str,
    Table,
)

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Any

    from panflute import Doc, Element


@dataclass(repr=False)
class Attribute(Filter):
    types: ClassVar[Any] = Table | Figure | Para

    def action(
        self,
        elem: Table | Figure | Para,
        doc: Doc | None,
    ) -> Table | Figure | Para:
        if isinstance(elem, Table):
            return set_attributes_table(elem)

        if isinstance(elem, Figure):
            return set_attributes_figure(elem)

        if isinstance(elem.content[0], Image):
            return set_attributes_image(elem)

        return set_attributes_math(elem)


def iter_attributes(elems: Iterable[Element]) -> Iterator[tuple[Element, bool]]:
    in_attr = False
    for elem in elems:
        if in_attr:
            yield elem, True
            if isinstance(elem, Str) and elem.text.endswith("}"):
                in_attr = False

        elif isinstance(elem, Str) and elem.text.startswith("{#"):
            yield elem, True
            in_attr = not elem.text.endswith("}")

        else:
            yield elem, False


def strip_elements(elems: Iterable[Element]) -> Iterator[Element]:
    elems = list(elems)
    spaces = [Space(), SoftBreak()]
    prev = None

    for i, elem in enumerate(elems):
        if prev is None:
            if elem in spaces:
                continue
            else:
                prev = elem
                if i == len(elems) - 1 and elem not in spaces:
                    yield elem

        elif elem in spaces and prev in spaces:
            continue

        else:
            yield prev
            if i == len(elems) - 1 and elem not in spaces:
                yield elem

            prev = elem


def split_attribute(elems: Iterable[Element]) -> tuple[list[Element], str]:
    content: list[Element] = []
    attr: list[Element] = []

    for elem, is_attr in iter_attributes(elems):
        if is_attr:
            attr.append(elem)
        else:
            content.append(elem)

    content = list(strip_elements(content))
    return content, pf.stringify(Plain(*attr))


def set_attributes(elem: Element, attrs: Iterable[Element]) -> list[Element] | None:
    keys = ["identifier", "classes", "attributes"]
    if any(getattr(elem, key, None) for key in keys):
        return None

    rest, text = split_attribute(attrs)
    code = pf.convert_text(f"`__panpdf__`{text}")[0].content[0]  # type:ignore

    for key in keys:
        setattr(elem, key, getattr(code, key))

    return rest


def set_attributes_table(table: Table) -> Table:
    if not table.caption.content:
        return table

    plain = table.caption.content[0]

    if isinstance(plain, Plain):
        elems = set_attributes(table, plain.content)

        if elems:
            table.caption = Caption(Plain(*elems))

    return table


def set_attributes_figure(figure: Figure) -> Figure:
    plain = figure.content[0]

    if isinstance(plain, Plain) and plain.content:
        image = plain.content[0]

        if isinstance(image, Image) and not image.identifier:
            image.identifier = figure.identifier

    return figure


def set_attributes_math(para: Para) -> Para:
    return Para(*_iter_elements(para.content))


def _iter_elements(elems: Iterable[Element]) -> Iterator[Element]:
    collected: list[Element] = []

    for elem in elems:
        if isinstance(elem, Math) and elem.format == "DisplayMath":
            yield from collected
            collected = [elem]

        elif not collected:
            yield elem

        elif isinstance(elem, Str) and elem.text.endswith("}"):
            collected[0] = Span(collected[0])
            set_attributes(collected[0], (*collected[1:], elem))

            yield collected[0]
            collected.clear()

        else:
            collected.append(elem)

    yield from collected


def split_image(para: Para) -> tuple[list[Image], list[Element]]:
    images: list[Image] = []
    rest = []
    for elem in para.content:
        if isinstance(elem, Image):
            images.append(elem)
        else:
            rest.append(elem)

    return images, rest


def set_attributes_image(para: Para) -> Figure:
    images, elems = split_image(para)
    figure = Figure(Plain(*images))
    rest = set_attributes(figure, elems)

    if rest and rest[0] == Str(":"):
        figure.caption = Caption(Plain(*strip_elements(rest[1:])))

    return figure
