from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from panflute import CodeBlock, RawBlock

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from panflute import Doc

# path = CONFIG_DIR / "include-in-header.tex"
# IN_HEADER = path.read_text(encoding="utf-8")
# pattern = r"(\\definecolor\{shadecolor\}\{.*?\}\{.*?\})"
# DEFAULT_SHADE = m.group(1) if (m := re.search(pattern, IN_HEADER)) else ""


@dataclass(repr=False)
class OutputCell(Filter):
    types: ClassVar[type[CodeBlock]] = CodeBlock

    def action(self, elem: CodeBlock, doc: Doc):  # noqa: ARG002
        if elem.classes != ["output"]:
            return elem

        elem.classes = ["text"]
        pre = "\\vspace{-0.5\\baselineskip}\\definecolor{shadecolor}{rgb}{1,1,0.9}%"
        return [RawBlock(pre, format="latex"), elem]

        # if DEFAULT_SHADE:
        #     elems += [RawBlock(DEFAULT_SHADE, format="latex")]
