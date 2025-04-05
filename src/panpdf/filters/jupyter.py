from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import nbstore.pgf
import yaml
from panflute import Doc, Image, Plain, RawInline

from panpdf.filters.filter import Filter
from panpdf.tools import add_metadata_list, convert_doc, create_temp_file

if TYPE_CHECKING:
    from nbstore import Store

PGF_PREFIX = "%% Creator: Matplotlib"


@dataclass(repr=False)
class Jupyter(Filter):
    types: ClassVar[type[Image]] = Image
    store: Store
    defaults: Path | None = None
    standalone: bool = False
    pandoc_path: Path | None = None
    pgf: bool = field(default=False, init=False)
    preamble: str = field(default="", init=False)

    def action(self, image: Image, doc: Doc) -> Image:
        url = image.url
        identifier = image.identifier

        if not identifier or (url and not url.endswith(".ipynb")):
            return image

        try:
            data = self.store.get_data(url, identifier)
        except ValueError:
            msg = f"[panpdf] Unknown url or id: url='{url}' id='{identifier}'"
            raise ValueError(msg) from None

        if not data:
            return image

        if not (url_or_text := create_image_file(data, standalone=self.standalone)):
            return image

        if not url_or_text.startswith(PGF_PREFIX):
            image.url = url_or_text
            return image

        text = nbstore.pgf.convert(url_or_text)

        if not self.preamble:
            self.preamble = get_preamble(text)

        if not self.standalone:
            image.url = text
            self.pgf = True
            return image

        image.url, text = create_image_file_pgf(
            text,
            defaults=self.defaults,
            preamble=self.preamble,
            pandoc_path=self.pandoc_path,
            description=f"Creating an image for {url}#{identifier}",
        )
        self.store.add_data(url, identifier, "application/pdf", text)
        self.store.save_notebook(url)
        return image

    def finalize(self, doc: Doc) -> None:
        if not self.pgf:
            return

        path = create_temp_file(f"\\usepackage{{pgf}}{self.preamble}", suffix=".tex")
        add_metadata_list(doc, "include-in-header", path.as_posix())


PREAMBLE_PATTERN = re.compile(
    r"^%% Matplotlib used the following preamble\n(.+?)\n%%\n",
    re.MULTILINE | re.DOTALL,
)

PREAMBLE = r"""
\def\mathdefault#1{#1}
\everymath=\expandafter{\the\everymath\displaystyle}
\makeatletter\@ifpackageloaded{underscore}{}{\usepackage[strings]{underscore}}\makeatother
"""


def get_preamble(text: str) -> str:
    if m := PREAMBLE_PATTERN.search(text):
        preamble = re.sub(r"^%%\s+", "", m.group(1), flags=re.MULTILINE)
        if "scrextend.sty" in preamble:  # for matplotlib 3.10.0
            return PREAMBLE
        return preamble

    return ""


def create_image_file(data: dict[str, str], *, standalone: bool = False) -> str | None:
    if text := data.get("text/pgf"):
        text_pgf = base64.b64decode(text).decode(encoding="utf-8")
    else:
        text = data.get("text/plain", "")
        text_pgf = text if text.startswith(PGF_PREFIX) else None

    if not standalone and text_pgf:
        return text_pgf

    if text := data.get("application/pdf"):
        return create_image_file_base64(text, ".pdf")

    if text := data.get("image/svg+xml"):
        url, _ = create_image_file_svg(text)
        return url

    if text_pgf:
        return text_pgf

    for mime, text in data.items():
        if mime.startswith("image/"):
            ext = mime.split("/")[1]
            return create_image_file_base64(text, f".{ext}")

    return None


def create_image_file_base64(text: str, suffix: str) -> str:
    data = base64.b64decode(text)
    path = create_temp_file(data, suffix=suffix)
    return path.as_posix()


def create_image_file_svg(xml: str) -> tuple[str, str]:
    import cairosvg

    path = create_temp_file(None, suffix=".pdf")
    file_obj = io.StringIO(xml)
    cairosvg.svg2pdf(file_obj=file_obj, write_to=path.as_posix())
    data = path.read_bytes()
    text = base64.b64encode(data).decode()
    return path.as_posix(), text


def create_image_file_pgf(
    text: str,
    *,
    defaults: Path | None = None,
    preamble: str = "",
    pandoc_path: Path | None = None,
    description: str = "",
) -> tuple[str, str]:
    doc = Doc(Plain(RawInline(text, format="latex")))
    defaults = create_defaults_for_standalone(defaults, preamble)

    path = create_temp_file(None, suffix=".pdf")
    extra_args = ["--defaults", defaults.as_posix(), "--output", path.as_posix()]

    convert_doc(
        doc,
        output_format="pdf",
        standalone=True,
        extra_args=extra_args,
        pandoc_path=pandoc_path,
        description=description,
    )

    data = path.read_bytes()
    text = base64.b64encode(data).decode()
    return path.as_posix(), text


def create_defaults_for_standalone(
    path: Path | None = None,
    preamble: str = "",
) -> Path:
    if path:
        with path.open("r", encoding="utf8") as f:
            defaults: dict[str, Any] = yaml.safe_load(f)
    else:
        path = Path()
        defaults = {}

    if "\\usepackage{fontspec}" in preamble:
        defaults.setdefault("pdf-engine", "xelatex")

    in_header = defaults.get("include-in-header", [])

    if isinstance(in_header, str):
        in_header = [in_header]

    path = create_temp_file(
        f"\\usepackage{{pgf}}{preamble}",
        suffix=".tex",
        dir=path.parent,
    )
    in_header.append(path.as_posix())
    defaults["include-in-header"] = in_header

    for toc in ["table-of-contents", "toc", "toc-depth"]:
        if toc in defaults:
            del defaults[toc]

    variables: dict[str, Any] = defaults.get("variables", {})
    documentclass = variables.get("documentclass")
    variables["documentclass"] = "standalone"
    defaults["variables"] = variables

    if documentclass:
        options: list[str] = variables.get("classoption", [])
        options.append(f"class={documentclass}")
        variables["classoption"] = options

    text = yaml.dump(defaults)
    return create_temp_file(text, suffix=".yaml", dir=path.parent)
