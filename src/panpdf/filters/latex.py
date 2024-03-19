from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from panflute import Cite, RawInline, Space, Str

from panpdf.filters.filter import Filter

CROSSREF_PATTERN = re.compile(r"^(\\\S+)(\s*)(\[@.+\])(\s*)$")

if TYPE_CHECKING:
    from panflute import Doc, Element


@dataclass(repr=False)
class Latex(Filter):
    types: ClassVar[type[RawInline]] = RawInline

    def action(self, elem: RawInline, doc: Doc):  # noqa: ARG002
        if elem.format != "tex":  # NOT 'latex'
            return elem

        if not (m := CROSSREF_PATTERN.match(elem.text)):
            return elem

        cmd, spacer, ref, suffix = m.groups()
        elems: list[Element] = [RawInline(cmd, format="tex")]  # NOT 'latex'

        if spacer:
            elems.append(Space())

        elems.append(Cite(Str(ref)))

        if suffix:
            elems.append(Space())

        return elems
