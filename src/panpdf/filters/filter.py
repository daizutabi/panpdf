from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import panflute as pf
from panflute import Doc, Element

if TYPE_CHECKING:
    from types import UnionType


@dataclass
class Filter:
    types: type[Element] | UnionType
    elements: list[Element] = field(default_factory=list, init=False, repr=False)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def _match(self, elem: Element) -> bool:
        if isinstance(elem, self.types):
            return self.match(elem)

        return False

    def match(self, elem: Element) -> bool:  # noqa: ARG002
        return True

    def _prepare(self, doc: Doc):
        def _append(elem: Element, doc: Doc):  # noqa: ARG001
            if self._match(elem):
                self.elements.append(elem)

        self.elements = []
        doc.walk(_append)

        if self.elements:
            self.prepare(doc)

    def prepare(self, doc: Doc):
        pass

    def _action(self, elem: Element, doc: Doc):
        if self._match(elem):
            return self.action(elem, doc)

        return None

    def action(self, elem: Element, doc: Doc):
        pass

    def _finalize(self, doc: Doc):
        if self.elements:
            self.finalize(doc)

    def finalize(self, doc: Doc):
        pass

    def run(self, doc: str | Doc | None = None) -> Doc:
        if isinstance(doc, str):
            doc = pf.convert_text(doc, standalone=True)  # type:ignore

        return pf.run_filter(self._action, self._prepare, self._finalize, doc=doc)  # type: ignore

    def set_metadata(self, doc: Doc, doc_from: Doc):
        pass
