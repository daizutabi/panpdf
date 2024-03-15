from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from panflute import CodeBlock, RawBlock

from panpdf.core.config import CONFIG_DIR
from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from panflute import Doc

path = CONFIG_DIR / "include-in-header.tex"
IN_HEADER = path.read_text(encoding="utf-8")
pattern = r"(\\definecolor\{shadecolor\}\{.*?\}\{.*?\})"
DEFAULT_SHADE = m.group(1) if (m := re.search(pattern, IN_HEADER)) else ""


@dataclass
class OutputCell(Filter):
    types: type[CodeBlock] = CodeBlock

    def action(self, elem: CodeBlock, doc: Doc):  # noqa: ARG002
        if elem.classes != ["output"]:
            return elem

        elem.classes = ["text"]
        pre = "\\vspace{-0.5\\baselineskip}\\definecolor{shadecolor}{rgb}{1,1,0.9}%"
        elems = [RawBlock(pre, format="latex"), elem]

        if DEFAULT_SHADE:
            elems += [RawBlock(DEFAULT_SHADE, format="latex")]

        return elems
