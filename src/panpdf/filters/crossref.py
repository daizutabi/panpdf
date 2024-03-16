from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from panflute import Cite, RawInline, Span, Str

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from types import UnionType

    from panflute import Doc, Element

CROSSREF_PATTERN = re.compile("^(sec|fig|tbl|eq):.+$")


@dataclass
class Crossref(Filter):
    types: UnionType = Span | Cite
    prefix: dict[str, list[Element]] = field(default_factory=dict)
    suffix: dict[str, list[Element]] = field(default_factory=dict)
    language: str = "en"

    def __post_init__(self):
        self.set_language(self.language)

    def action(self, elem: Span | Cite, doc: Doc) -> list[Element] | None:  # noqa: ARG002
        if isinstance(elem, Span):
            return list(elem.content)

        if isinstance(elem, Cite) and elem.citations:
            id_ = elem.citations[0].id  # type:ignore
            if CROSSREF_PATTERN.match(id_):
                return self.create_ref(id_)

        return None

    def create_ref(self, id_: str) -> list[Element]:
        ref = RawInline(f"\\ref{{{id_}}}", format="latex")
        kind = id_.split(":")[0]
        prefix = self.prefix.get(kind, [])
        suffix = self.suffix.get(kind, [])
        return [*prefix, ref, *suffix]

    def set_language(self, language: str):
        self.language = language
        if self.language.lower().startswith("ja"):
            self.set_prefix("fig", "図")
            self.set_prefix("tbl", "表")
            self.set_prefix("eq", "式")

        else:
            self.set_prefix("fig", "Fig.")
            self.set_prefix("tbl", "Table")
            self.set_prefix("eq", "Eq.")

    def set_prefix(self, kind: str, prefix: str):
        self.prefix[kind] = [Str(prefix), RawInline("~", format="latex")]

    def set_suffix(self, kind: str, suffix: str):
        self.suffix[kind] = [Str(suffix)]
