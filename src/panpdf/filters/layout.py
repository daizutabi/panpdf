from __future__ import annotations

import atexit
import base64
import io
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import partial
from itertools import chain
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import TYPE_CHECKING

import panflute as pf
from panflute import (
    Caption,
    Code,
    Doc,
    Element,
    Figure,
    Image,
    Math,
    Para,
    Plain,
    RawInline,
    SoftBreak,
    Space,
    Span,
    Str,
    Table,
)

from panpdf import utils
from panpdf.config import CONFIG_DIR, create_standalone
from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import UnionType


@dataclass
class Layout(Filter):
    types: UnionType = Math | Table | Figure
    external: bool = False

    def __post_init__(self) -> None:
        self.path_images = Path.cwd() / "_images"  # Path("_images") ?
        self.path_lualatex = Path.cwd() / "_lualatex"  # Path("_lualatex") ?
        self.path_standalone = Path("standalone.tex")

    def prepare(self, doc: Doc) -> None:  # noqa: ARG002
        self.path_images.mkdir(exist_ok=True)
        self.path_lualatex.mkdir(exist_ok=True)

        if self.external:
            text = create_standalone()
            self.path_standalone.write_text(text, encoding="utf8")

        atexit.register(self.delete)

    def delete(self):
        if self.path_lualatex.exists():
            for file in self.path_lualatex.iterdir():
                file.unlink()

            self.path_lualatex.rmdir()

        if self.path_standalone.exists():
            self.path_standalone.unlink()

    def action(self, elem: Math | Table | Figure, doc: Doc) -> Math | RawInline | Table | Figure:  # noqa: ARG002
        if isinstance(elem, Math):
            return convert_math(elem)

        if isinstance(elem, Table):
            return convert_table(elem)

        return convert_figure(elem, external=self.external)


def convert_math(math: Math) -> Math | RawInline:
    if (span := math.parent) and isinstance(span, Span) and (id_ := span.identifier):
        env = "equation" if "\\\\" not in math.text else "eqnarray"
        text = f"\\begin{{{env}}}\n{math.text}"
        text += f"\\label{{{id_}}}\n"
        text += f"\\end{{{env}}}\n"
        return RawInline(text, format="latex")

    return math


def convert_table(table: Table) -> Table:
    if table.caption and table.identifier:
        label = f"\\label{{{table.identifier}}}"
        plain = table.caption.content[0]
        plain.content.insert(0, RawInline(label, format="latex"))  # type:ignore

    return table


def get_images(figure: Figure) -> list[Image]:
    plain = figure.content[0]
    if not isinstance(plain, Plain):
        return []

    return [image for image in plain.content if isinstance(image, Image)]


def convert_figure(figure: Figure, *, external: bool = False) -> Figure:
    if not (images := get_images(figure)):
        return figure

    images = [convert_image(image, external=external) for image in images]

    figure.content = [Plain(*images)]

    return create_figure(figure)


def convert_image(image: Image, *, external: bool) -> Image:
    if "panpdf-pgf" in image.classes and not external:
        return image

    for fmt in ["pgf", "pdf", "base64", "svg"]:
        if f"panpdf-{fmt}" in image.classes:
            image.url = create_image_file(image)
            break

    return image


def create_image_file(image: Image) -> str:
    root = Path.cwd() / "_images"
    workdir = Path.cwd() / "_lualatex"

    if "panpdf-pgf" in image.classes:
        return create_image_file_pgf(image, root, workdir)

    if "panpdf-pdf" in image.classes:
        return create_image_file_pdf(image, root)

    if "panpdf-base64" in image.classes:
        return create_image_file_base64(image, root)

    return create_image_file_svg(image, root)


def create_image_file_pgf(image: Image, root: Path, workdir: Path) -> str:
    id_ = image.identifier.replace("fig:", "")
    name = Path(f"{id_}.tex")
    path_tex = root / name
    path_pdf = root / f"{id_}.pdf"
    path = Path("standalone.tex")

    if not path.exists():
        path = CONFIG_DIR / path

    text = path.read_text(encoding="utf-8").replace("$body$", image.url)
    cmds = ["ptex2pdf", "-u", "-l"] if "uplatex" in text.split()[0] else ["lualatex"]
    cmds.extend(["--halt-on-error", str(name)])

    if path_tex.exists() and path_pdf.exists() and text == path_tex.read_text(encoding="utf8"):
        return path_pdf.as_posix()

    # spinner = halo.Halo(f"Creating {path_pdf.name}")
    # spinner.start()
    curdir = os.getcwd()
    os.chdir(workdir)

    name.write_text(text, encoding="utf8")
    r = subprocess.run(cmds, stdout=PIPE, stderr=STDOUT, check=False)

    if r.returncode:
        # spinner.fail()
        sys.exit()
    else:
        # spinner.succeed()
        shutil.move(name, path_tex)
        shutil.move(str(name).replace(".tex", ".pdf"), path_pdf)

    os.chdir(curdir)
    return path_pdf.as_posix()


def create_image_file_base64(image: Image, root: Path) -> str:
    ext = image.url.split("/")[1].split(";")[0]
    text = image.url[image.url.index("base64,") + 7 :]
    id_ = image.identifier.replace("fig:", "")
    path = root / f"{id_}.{ext}"
    data = base64.b64decode(text)
    path.write_bytes(data)
    return path.as_posix()


def create_image_file_pdf(image: Image, root: Path) -> str:
    id_ = image.identifier.replace("fig:", "")
    path = root / f"{id_}.pdf"
    data = base64.b64decode(image.url)
    path.write_bytes(data)
    return path.as_posix()


def create_image_file_svg(image: Image, root: Path) -> str:  # noqa: ARG001
    raise NotImplementedError
    # file_obj = io.StringIO(image.url)
    # id = image.identifier.replace("fig:", "")
    # write_to = str(root / f"{id}.pdf")
    # cairosvg.svg2pdf(file_obj=file_obj, write_to=write_to)
    # return write_to.replace("\\", "/")


def create_figure_from_image(image: Image) -> Figure:
    if "panpdf-pgf" in image.classes and not image.url.endswith(".pdf"):
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

    head, tail = tex.split("\\caption{XXX}")
    head = head.replace("\\begin{figure}", f"\\begin{{{env}}}{{{width}}}")
    tail = tail.replace("\\end{figure}", f"\\end{{{env}}}")

    yield RawInline(f"{head}\\caption{{", format="latex")
    yield from image.content
    yield RawInline(f"}}{tail}", format="latex")


def create_figure(figure: Figure) -> Figure:
    images = get_images(figure)
    n = len(images)

    if n == 1:
        return create_figure_from_image(images[0])

    if caption := figure.caption:
        env = "subfigure"
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

    identifier = figure.identifier
    return Figure(Plain(*elems), caption=caption, identifier=identifier)


def get_width(image: Image, name: str) -> str:
    width = image.attributes.get(name, "")

    if isinstance(width, str) and width.endswith("%"):
        width = f"{int(width[:-1])/100}\\columnwidth"

    return width
