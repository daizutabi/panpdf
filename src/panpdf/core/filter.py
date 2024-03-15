from dataclasses import dataclass, field

import panflute as pf
from panflute import Doc, Element


@dataclass
class Filter:
    """Filter class."""

    types: type[Element] | tuple[type[Element], ...] = ()
    elements: list[Element] = field(default_factory=list, init=False, repr=False)

    def _match(self, elem: Element) -> bool:
        if not self.types or isinstance(elem, self.types):
            return self.match(elem)
        return False

    def match(self, elem: Element) -> bool:
        return True

    def _prepare(self, doc: Doc):
        def _append(elem: Element, doc: Doc):
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

    def run(self, doc: str | Doc | None = None):
        if isinstance(doc, str):
            doc = pf.convert_text(doc, standalone=True)  # type:ignore
        return pf.run_filter(self._action, self._prepare, self._finalize, doc=doc)

    def set_metadata(self, doc: Doc, doc_from: Doc):
        pass
