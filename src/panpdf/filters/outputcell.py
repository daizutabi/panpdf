import re
from dataclasses import dataclass

import panflute as pf
from panflute import CodeBlock, Doc, Element

from panpdf.core.config import RESOURCE_DIR
from panpdf.core.filter import Filter

path = RESOURCE_DIR / "include-in-header.tex"
IN_HEADER = path.read_text(encoding="utf-8")
pattern = r"(\\definecolor\{shadecolor\}\{.*?\}\{.*?\})"
if m := re.search(pattern, IN_HEADER):
    DEFAULT_SHADE = m.group(1)
else:
    DEFAULT_SHADE = ""


@dataclass
class OutputCell(Filter):
    types: tuple[type[Element], ...] = (CodeBlock,)

    def action(self, elem: CodeBlock, doc: Doc):
        if elem.classes != ["output"]:
            return elem
        elem.classes = ["text"]
        pre = "\\vspace{-0.5\\baselineskip}\\definecolor{shadecolor}{rgb}{1,1,0.9}%"
        elems = [pf.RawBlock(pre, format="latex"), elem]
        if DEFAULT_SHADE:
            elems += [pf.RawBlock(DEFAULT_SHADE, format="latex")]
        return elems
