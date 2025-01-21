from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import panflute as pf
from panflute import Doc, Element

if TYPE_CHECKING:
    from typing import Any


@dataclass(repr=False)
class Filter:
    types: type[Element] | Any = Element
    elements: list[Element] = field(default_factory=list, init=False)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def _prepare(self, doc: Doc):
        self.prepare(doc)

    def prepare(self, doc: Doc):
        pass

    def _action(self, elem: Element, doc: Doc):
        if isinstance(elem, self.types):
            elems = self.action(elem, doc)

            if elems != []:
                self.elements.append(elem)

            return elems

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
