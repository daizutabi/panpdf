from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from panflute import Cite, RawInline, Str

from panpdf.filters.filter import Filter
from panpdf.tools import get_metadata_str

if TYPE_CHECKING:
    from panflute import Doc, Element

CROSSREF_PATTERN = re.compile("^(sec|fig|tbl|eq):.+$")


@dataclass(repr=False)
class Crossref(Filter):
    types: ClassVar[type[Cite]] = Cite
    prefix: dict[str, list[Element]] = field(default_factory=dict)
    suffix: dict[str, list[Element]] = field(default_factory=dict)

    def prepare(self, doc: Doc) -> None:
        name = get_metadata_str(doc, "reference-figure-name") or "Fig."
        self.set_prefix("fig", name)

        name = get_metadata_str(doc, "reference-table-name") or "Table"
        self.set_prefix("tbl", name)

        name = get_metadata_str(doc, "reference-equation-name") or "Eq."
        self.set_prefix("eq", name)

    def action(self, elem: Cite, doc: Doc) -> list[Element] | None:
        if elem.citations:
            identifier = elem.citations[0].id  # type:ignore
            if CROSSREF_PATTERN.match(identifier):
                return self.create_ref(identifier)

        return None

    def create_ref(self, identifier: str) -> list[Element]:
        if identifier.endswith("_"):
            identifier = identifier[:-1]
            bare = True
        else:
            bare = False

        ref = RawInline(f"\\ref{{{identifier}}}", format="latex")

        if bare:
            return [ref]

        kind = identifier.split(":")[0]
        prefix = self.prefix.get(kind, [])
        suffix = self.suffix.get(kind, [])
        return [*prefix, ref, *suffix]

    def set_prefix(self, kind: str, prefix: str) -> None:
        self.prefix[kind] = [Str(prefix), RawInline("~", format="latex")]

    def set_suffix(self, kind: str, suffix: str) -> None:
        self.suffix[kind] = [Str(suffix)]
