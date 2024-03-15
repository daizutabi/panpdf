from __future__ import annotations

import atexit
import base64
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import partial
from itertools import chain
from pathlib import Path
from subprocess import PIPE, STDOUT

from panflute import (
    Code,
    Doc,
    Element,
    Image,
    Math,
    Para,
    RawInline,
    SoftBreak,
    Space,
    Span,
    Str,
    Table,
)

from panpdf import utils
from panpdf.core.config import CONFIG_DIR, create_standalone
from panpdf.filters.filter import Filter


@dataclass
class Layout(Filter):
    types: tuple[type[Element], ...] = (Para, Table, Math)
    external: bool = False

    def prepare(self, doc: Doc):  # noqa: ARG002
        path_images = Path.cwd() / "_images"
        path_images.mkdir(exist_ok=True)

        path_lualatex = Path.cwd() / "_lualatex"
        path_lualatex.mkdir(exist_ok=True)

        path_standalone = Path("standalone.tex")
        if self.external:
            text = create_standalone()
            path_standalone.write_text(text, encoding="utf8")

        def delete():
            if path_lualatex.exists():
                for file in path_lualatex.iterdir():
                    file.unlink()
                path_lualatex.rmdir()

            if path_standalone.exists():
                path_standalone.unlink()

        atexit.register(delete)
        return delete

    def action(self, elem: Math | Table | Para, doc: Doc):  # noqa: ARG002
        if isinstance(elem, Math):
            return convert_math(elem)

        if isinstance(elem, Table):
            return convert_table(elem)

        return convert_para(elem, external=self.external)


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


def split_images_caption(para: Para) -> tuple[list[Image], list[Element] | None]:
    images: list[Image] = []
    is_float = False

    for k, elem in enumerate(para.content):
        if isinstance(elem, Image):
            images.append(elem)
            is_float = True

        elif is_float and elem == Str(":") and elem.next == Space():
            return images, list(para.content[k + 2 :])  # type:ignore

        elif not isinstance(elem, SoftBreak):
            is_float = False

    return images, None


def convert_para(para: Para, *, external: bool = False) -> Para:
    images, caption = split_images_caption(para)
    if not images:
        return para

    for image in images:
        n = len(images)
        set_width(image, n)
        set_url(image, multicolumn=n > 1, external=external)

    if len(images) == 1:
        return create_para_figure(images, create_figure_content)

    if caption:
        func = partial(minipage, name="subfigure")  # type: ignore
        suffix = create_suffix(caption)
        return create_para_figure(images, func, [suffix])

    return create_para_figure(images, minipage)


def set_width(image: Image, n: int):
    width = image.attributes.get("width", "")
    if not width and n > 1:
        image.attributes["width"] = f"{int(100/n)}%"


def get_width(image: Image, name: str = "width") -> str:
    width = image.attributes.get(name, "")
    if isinstance(width, str) and width.endswith("%"):
        width = f"{int(width[:-1])/100}\\columnwidth"

    return width


def set_url(image: Image, *, multicolumn: bool, external: bool = False):
    if "panpdf-pgf" in image.classes:
        if external:
            image.url = create_image_file(image)
        else:
            return  # TODO: width

    else:
        for cls in ["base64", "svg", "pdf"]:
            if f"panpdf-{cls}" in image.classes:
                image.url = create_image_file(image)
                break

    options = ""
    if not multicolumn and (width := get_width(image)):
        options = f"[width={width}]"

    image.url = f"\\includegraphics{options}{{{image.url}}}%"  # Don't delete '%'


def create_para_figure(images: list[Image], func, suffix=None) -> Para:
    begin = RawInline("\\begin{figure}\n\\centering\n", format="latex")
    contents = [func(image) for image in images]
    content = list(chain.from_iterable(contents))
    end = RawInline("\\end{figure}\n", format="latex")
    return Para(begin, *content, *(suffix or []), end)


def R(text):  # noqa: N802
    return RawInline(text, format="latex")


def create_caption(id_: str, caption: list[Element]) -> Span:
    label = R(f"}}\\label{{{id_}}}\n")
    return Span(R("\\caption{"), *caption, label, identifier=id_)


def create_figure_content(image: Image) -> list[Element]:
    body = R(f"\\centering\n{image.url}\n")
    caption = create_caption(image.identifier, list(image.content))
    return [body, caption]


def minipage(image, name="minipage") -> list[Element]:
    width = get_width(image)
    begin = RawInline(f"\\begin{{{name}}}[t]{{{width}}}\n", format="latex")
    content = create_figure_content(image)
    end = RawInline(f"\\end{{{name}}}%\n", format="latex")
    elems = [begin, *content, end]

    if hspace := get_width(image, "hspace"):
        elems += [RawInline(f"\\hspace{{{hspace}}}%\n", format="latex")]

    return elems


def create_suffix(caption: list[Element]) -> Span:
    code = Code("")
    span = utils.set_attributes(code, Span(*caption))
    return create_caption(code.identifier, list(span.content))  # type:ignore


def create_image_file(image: Image) -> str:
    root = Path.cwd() / "_images"
    workdir = Path.cwd() / "_lualatex"

    if "panpdf-latex" in image.classes:
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
    text_old = ""

    if path_tex.exists() and path_pdf.exists():
        text_old = path_tex.read_text(encoding="utf8")

    # spinner = halo.Halo(f"Creating {path_pdf.name}")
    # spinner.start()
    if text != text_old:
        curdir = os.getcwd()
        os.chdir(workdir)
        name.write_text(text, encoding="utf8")
        r = subprocess.run(
            [*cmds, "--halt-on-error", str(name)], stdout=PIPE, stderr=STDOUT, check=False
        )
        if r.returncode:
            # spinner.fail()
            sys.exit()
        else:
            # spinner.succeed()
            shutil.move(name, path_tex)
            shutil.move(str(name).replace(".tex", ".pdf"), path_pdf)
        os.chdir(curdir)
    else:
        pass
        # spinner.succeed()
    return str(path_pdf).replace("\\", "/")


def create_image_file_base64(image: Image, root: Path) -> str:
    ext = image.url.split("/")[1].split(";")[0]
    text = image.url[image.url.index("base64,") + 7 :]
    id_ = image.identifier.replace("fig:", "")
    path = root / f"{id_}.{ext}"
    data = base64.b64decode(text)
    path.write_bytes(data)
    return str(path).replace("\\", "/")


def create_image_file_pdf(image: Image, root: Path) -> str:
    id_ = image.identifier.replace("fig:", "")
    path = root / f"{id_}.pdf"
    data = base64.b64decode(image.url)
    path.write_bytes(data)
    return str(path).replace("\\", "/")


def create_image_file_svg(image: Image, root: Path) -> str:  # noqa: ARG001
    raise NotImplementedError
    # file_obj = io.StringIO(image.url)
    # id = image.identifier.replace("fig:", "")
    # write_to = str(root / f"{id}.pdf")
    # cairosvg.svg2pdf(file_obj=file_obj, write_to=write_to)
    # return write_to.replace("\\", "/")
