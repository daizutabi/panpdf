from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import panflute as pf
from panflute import (
    Caption,
    Doc,
    Element,
    Figure,
    Image,
    Math,
    Plain,
    RawInline,
    Span,
    Str,
)

from panpdf.filters.filter import Filter
from panpdf.filters.jupyter import PGF_PREFIX
from panpdf.tools import add_metadata_list, create_temp_file

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


@dataclass(repr=False)
class Layout(Filter):
    types: ClassVar[Any] = Span | Figure

    def action(
        self,
        elem: Span | Figure,
        doc: Doc,
    ) -> Span | RawInline | Figure | Plain:
        if isinstance(elem, Span):
            return convert_span(elem)

        return convert_figure(elem, doc)

    def finalize(self, doc: Doc) -> None:
        if doc.metadata.pop("__subcaption__", None):
            path = create_temp_file("\\usepackage{subcaption}", suffix=".tex")
            add_metadata_list(doc, "include-in-header", path.as_posix())


def convert_span(span: Span) -> Span | RawInline:
    math = span.content[0]
    if isinstance(math, Math) and span.identifier:
        env = "equation" if "\\\\" not in math.text else "eqnarray"
        text = f"\\begin{{{env}}}\n{math.text}"
        text += f"\\label{{{span.identifier}}}\n"
        text += f"\\end{{{env}}}\n"
        return RawInline(text, format="latex")

    return span


def convert_figure(figure: Figure, doc: Doc) -> Figure | Plain:
    images = get_images(figure)
    n = len(images)

    if n == 1:
        figure = create_figure_from_image(images[0])
        if "cell" in images[0].classes:
            return create_cell_plain(figure.content[0])  # type: ignore

        return figure

    if (caption := figure.caption) and caption.content:
        env = "subfigure"
        doc.metadata["__subcaption__"] = True
    else:
        env = "minipage"
        caption = Caption()

    elems = []
    for image in images:
        width = get_width(image, "cwidth") or f"{0.95 / n}\\columnwidth"
        elems.extend(iter_subfigure_elements(image, env, width))

        if hspace := get_width(image, "hspace"):
            elems.append(RawInline(f"\n\\hspace{{{hspace}}}%", format="latex"))

        elems.append(RawInline("\n", format="latex"))

    if identifier := figure.identifier:
        return Figure(Plain(*elems), caption=caption, identifier=identifier)

    begin = RawInline("\\begin{figure}\n\\centering\n", format="latex")
    end = RawInline("\\end{figure}\n", format="latex")
    return Plain(begin, *elems, end)


def create_cell_plain(plain: Plain) -> Plain:
    image = plain.content[0]
    vspace = RawInline("\\vspace{0.4\\baselineskip}", format="latex")
    begin = RawInline("\\begin{quote}\n", format="latex")
    end = RawInline("\\end{quote}\n", format="latex")
    return Plain(vspace, begin, image, end)


def get_images(figure: Figure) -> list[Image]:
    plain = figure.content[0]
    if not isinstance(plain, Plain):
        return []

    return [image for image in plain.content if isinstance(image, Image)]


def create_figure_from_image(image: Image) -> Figure:
    if image.url.startswith(PGF_PREFIX):
        plain = Plain(RawInline(image.url, format="latex"))
    else:
        plain = Plain(image)

    caption = Caption(Plain(*image.content))
    identifier = image.identifier
    return Figure(plain, caption=caption, identifier=identifier)


def iter_subfigure_elements(image: Image, env: str, width: str) -> Iterator[Element]:
    fig = create_figure_from_image(image)
    fig.caption = Caption(Plain(Str("XXX")))

    tex = pf.convert_text(fig, input_format="panflute", output_format="latex")
    if not isinstance(tex, str):
        return

    tex = tex.replace(",height=\\textheight", "")
    head, tail = tex.split("\\caption{XXX}")
    head = head.replace("\\begin{figure}", f"\\begin{{{env}}}{{{width}}}")
    tail = tail.replace("\\end{figure}", f"\\end{{{env}}}")

    yield RawInline(f"{head}\\caption{{", format="latex")
    yield from image.content
    yield RawInline(f"}}{tail}", format="latex")


def get_width(image: Image, name: str) -> str:
    width = image.attributes.get(name, "")

    if isinstance(width, str) and width.endswith("%"):
        width = f"{int(width[:-1]) / 100}\\columnwidth"

    return width
