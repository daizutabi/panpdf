from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from panflute import Cite, Doc, Math, RawInline, Span, Str

from panpdf.filters.filter import Filter
from panpdf.utils import get_metadata

if TYPE_CHECKING:
    from types import UnionType

    from panflute import Doc, Element

CROSSREF_PATTERN = re.compile("^(sec|fig|tbl|eq):.+$")


@dataclass(repr=False)
class Crossref(Filter):
    types: ClassVar[UnionType] = Span | Cite
    prefix: dict[str, list[Element]] = field(default_factory=dict)
    suffix: dict[str, list[Element]] = field(default_factory=dict)

    def prepare(self, doc: Doc):
        name = get_metadata(doc, "figure-ref-name") or "Fig."
        self.set_prefix("fig", name)

        name = get_metadata(doc, "table-ref-name") or "Table"
        self.set_prefix("tbl", name)

        name = get_metadata(doc, "equation-ref-name") or "Eq."
        self.set_prefix("eq", name)

    def action(self, elem: Span | Cite, doc: Doc) -> list[Element] | Span | None:  # noqa: ARG002
        if isinstance(elem, Span):
            if isinstance(elem.content[0], Math):
                return list(elem.content)
            return elem

        if isinstance(elem, Cite) and elem.citations:
            identifier = elem.citations[0].id  # type:ignore
            if CROSSREF_PATTERN.match(identifier):
                return self.create_ref(identifier)

        return None

    def create_ref(self, identifier: str) -> list[Element]:
        ref = RawInline(f"\\ref{{{identifier}}}", format="latex")
        kind = identifier.split(":")[0]
        prefix = self.prefix.get(kind, [])
        suffix = self.suffix.get(kind, [])
        return [*prefix, ref, *suffix]

    def set_prefix(self, kind: str, prefix: str):
        self.prefix[kind] = [Str(prefix), RawInline("~", format="latex")]

    def set_suffix(self, kind: str, suffix: str):
        self.suffix[kind] = [Str(suffix)]
