from __future__ import annotations

from dataclasses import dataclass, field

import panflute as pf
from panflute import Cite, Doc, Element, Header, Image, Span, Table

from panpdf.filters.filter import Filter


@dataclass
class Crossref(Filter):
    types: tuple[type[Element], ...] = (Header, Image, Table, Span, Cite)
    identifiers: list[str] = field(default_factory=list)
    prefix: dict[str, list[Element]] = field(default_factory=dict)
    suffix: dict[str, list[Element]] = field(default_factory=dict)
    language: str = "en"

    def prepare(self, doc: Doc):  # noqa: ARG002
        self.set_language(self.language)
        for elem in self.elements:
            if isinstance(elem, Header | Image | Table | Span) and elem.identifier:
                self.identifiers.append(elem.identifier)

    def action(self, elem: Header | Image | Table | Span | Cite, doc: Doc):  # noqa: ARG002
        if isinstance(elem, Cite) and elem.citations:
            if (id_ := elem.citations[0].id) in self.identifiers:  # type:ignore
                return self.create_ref(id_)

        elif isinstance(elem, Span):
            return list(elem.content)

        return None

    def create_ref(self, id_: str):
        ref = pf.RawInline(f"\\ref{{{id_}}}", format="latex")
        if ":" in id_:
            kind = id_.split(":")[0]
            prefix = self.prefix.get(kind, [])
            suffix = self.suffix.get(kind, [])
            return [*prefix, ref, *suffix]

        return [ref]

    def set_language(self, language: str):
        self.language = language
        if language.lower().startswith("ja"):
            self.set_prefix_suffix("fig", "図", "")
            self.set_prefix_suffix("tbl", "表", "")
            self.set_prefix_suffix("eq", "式", "")
        elif language.lower().startswith("en"):
            self.set_prefix_suffix("fig", "Fig.", "")
            self.set_prefix_suffix("tbl", "Table", "")
            self.set_prefix_suffix("eq", "Eq.", "")

    def set_prefix_suffix(self, kind: str, prefix: str, suffix: str):
        if prefix:
            self.prefix[kind] = [pf.Str(prefix), pf.RawInline("~", format="latex")]
        if suffix:
            self.suffix[kind] = [pf.Str(suffix)]
