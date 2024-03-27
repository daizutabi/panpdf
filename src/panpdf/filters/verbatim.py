from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from panflute import CodeBlock, RawBlock

from panpdf.filters.filter import Filter
from panpdf.tools import add_metadata_list, create_temp_file

if TYPE_CHECKING:
    from panflute import Doc, Element

DEFAULT_SHADE_COLOR = "\\definecolor{shadecolor}{RGB}{240,240,250}"


@dataclass(repr=False)
class Verbatim(Filter):
    types: ClassVar[type[CodeBlock]] = CodeBlock

    def prepare(self, doc: Doc):
        path = create_in_header()
        add_metadata_list(doc, "include-in-header", path.as_posix())

    def action(self, elem: CodeBlock, doc: Doc) -> CodeBlock | list[Element]:  # noqa: ARG002
        if "output" not in elem.classes:
            return elem

        elem.classes.pop(elem.classes.index("output"))
        pre = "\\vspace{-0.5\\baselineskip}\\definecolor{shadecolor}{rgb}{1,1,0.9}%"
        return [RawBlock(pre, format="latex"), elem, RawBlock(DEFAULT_SHADE_COLOR, format="latex")]


def create_in_header():
    text = r"""
    \ifdefined\Shaded
    \usepackage{framed}
    \renewenvironment{Shaded}{\begin{quotation}\begin{snugshade}\linespread{0.9}}%
    {\end{snugshade}\end{quotation}}
    \definecolor{shadecolor}{RGB}{240,240,250}
    \DefineVerbatimEnvironment{Highlighting}{Verbatim}%
    {commandchars=\\\{\},fontsize=\small,numbers=left}
    """
    text = inspect.cleandoc(text)
    text = f"{text}\n{DEFAULT_SHADE_COLOR}\n\\fi"
    return create_temp_file(text, suffix=".tex")
