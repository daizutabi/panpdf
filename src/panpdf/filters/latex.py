from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from panflute import Cite, RawInline, Space, Str

from panpdf.filters.filter import Filter

CROSSREF_PATTERN = re.compile(r"^(\\\S+)(\s*)(\[@.+\])(\s*)$")

if TYPE_CHECKING:
    from panflute import Doc, Element


@dataclass
class Latex(Filter):
    types: tuple[type[Element], ...] = (RawInline,)

    def action(self, elem: RawInline, doc: Doc):  # noqa: ARG002
        if elem.format != "tex":
            return elem

        if not (m := CROSSREF_PATTERN.match(elem.text)):
            return elem

        cmd, spacer, ref, suffix = m.groups()
        elems: list[Element] = [RawInline(cmd, format="tex")]

        if spacer:
            elems.append(Space())

        elems.append(Cite(Str(ref)))

        if suffix:
            elems.append(Space())

        return elems
