from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from panflute import CodeBlock, RawBlock

from panpdf.filters.filter import Filter
from panpdf.tools import add_metadata_list, create_temp_file

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from panflute import Doc, Element

CONFIG: dict[str, str] = {"fontsize": "\\small"}  # , "baselinestretch": "auto"}


@dataclass(repr=False)
class Verbatim(Filter):
    types: ClassVar[type[CodeBlock]] = CodeBlock

    def __post_init__(self) -> None:
        self.shaded = False

    def action(self, elem: CodeBlock, doc: Doc) -> CodeBlock | list[Element]:
        self.shaded = True

        if "title" in elem.attributes:
            return create_title(elem)

        if "output" in elem.classes:
            return create_output(elem)

        return create_default(elem)

    def finalize(self, doc: Doc) -> None:
        if self.shaded:
            path = create_header()
            add_metadata_list(doc, "include-in-header", path.as_posix())


def create_output(code: CodeBlock) -> list[Element]:
    code.classes.pop(code.classes.index("output"))

    return [vspace(), *create_code_block(code, OUTPUT_SHADE_COLOR)]


def create_title(code: CodeBlock) -> list[Element]:
    attrs = {"formatcom": f"\\color{{{TITLE_COLOR}}}\\bfseries"}
    title = CodeBlock(code.attributes.pop("title"), attributes=attrs)

    return [
        *create_code_block(title, TITLE_SHADE_COLOR),
        vspace(),
        *create_code_block(code, DEFAULT_SHADE_COLOR),
    ]


def create_default(code: CodeBlock) -> list[Element]:
    return create_code_block(code, DEFAULT_SHADE_COLOR)


def create_code_block(code: CodeBlock, rgb: Iterable) -> list[Element]:
    env = define_verbatim_environment(code.attributes)
    color = define_shade_color(rgb)

    if not code.classes:
        code.classes = ["text"]

    return [RawBlock(f"{env}{color}", format="latex"), code]


def vspace() -> RawBlock:
    return RawBlock("\\vspace{-0.5\\baselineskip}", format="latex")


TITLE_SHADE_COLOR = (0.9, 0.9, 1)
DEFAULT_SHADE_COLOR = (0.94, 0.94, 0.94)
OUTPUT_SHADE_COLOR = (1, 1, 0.9)
TITLE_COLOR = "NavyBlue"


def define_verbatim_environment(attrs: dict[str, str]) -> str:
    text = r"\DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\}"
    args = []
    for key, value in attrs.items():
        args.append(f"{key}={value}")
        if key in CONFIG:
            CONFIG[key] = value

    for key, value in CONFIG.items():
        if key not in attrs:
            args.append(f"{key}={value}")

    args_str = ",".join(args)
    return f"{text},{args_str}}}"


def define_shade_color(rgb: Iterable) -> str:
    rgb_str = ",".join(str(x) for x in rgb)
    return f"\\definecolor{{shadecolor}}{{rgb}}{{{rgb_str}}}"


def create_header(linespread: float = 0.85) -> Path:
    text = (
        "\\ifdefined\\Shaded\\usepackage{framed}"
        "\\renewenvironment{Shaded}{\\begin{quote}\\begin{snugshade}\\linespread{"
        f"{linespread}"
        "}}{\\end{snugshade}\\end{quote}}\\fi"
    )
    return create_temp_file(text, suffix=".tex")
