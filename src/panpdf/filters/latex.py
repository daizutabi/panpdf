import re
from dataclasses import dataclass

from panflute import Cite, Doc, Element, RawInline, Space, Str

from panpdf.core.filter import Filter

CROSSREF_PATTERN = re.compile(r"^(\\\S+)(\s*)(\[@.+\])(\s*)$")


@dataclass
class Latex(Filter):
    types: tuple[type[Element], ...] = (RawInline,)

    def action(self, elem: RawInline, doc: Doc):
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
