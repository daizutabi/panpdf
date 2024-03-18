from __future__ import annotations

import atexit
import base64
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import yaml
from panflute import Doc, Image, Plain, RawInline

from panpdf.filters.filter import Filter
from panpdf.panflute import convert_text
from panpdf.stores import Store

PGF_PREFIX = "%% Creator: Matplotlib"


@dataclass(repr=False)
class Jupyter(Filter):
    types: ClassVar[type[Image]] = Image
    defaults: Path
    standalone: bool = False
    pandoc_path: Path | None = None
    store: Store = field(default_factory=Store)

    def action(self, image: Image, doc: Doc) -> Image:  # noqa: ARG002
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

        if not url_or_text.startswith(PGF_PREFIX) or not self.standalone:
            image.url = url_or_text
            return image

        image.url, text = create_image_file_pgf(url_or_text, self.defaults, self.pandoc_path)
        self.store.add_data(url, identifier, "application/pdf", text)
        self.store.save_notebook(url)
        return image

    def create_image_file_pgf(self, image: Image, text: str) -> Image:
        image.url = text
        return image


def create_image_file(data: dict[str, str], *, standalone: bool = False) -> str | None:
    text = data.get("text/plain", "")
    text_pgf = text if text.startswith(PGF_PREFIX) else None

    if not standalone and text_pgf:
        return text_pgf

    if text := data.get("application/pdf"):
        return create_image_file_base64(text, ".pdf")

    if text := data.get("image/svg+xml"):
        return create_image_file_svg(text)

    if text_pgf:
        return text_pgf

    for mime, text in data.items():
        if mime.startswith("image/"):
            ext = mime.split("/")[1]
            return create_image_file_base64(text, f".{ext}")

    return None


def create_image_file_base64(text: str, suffix: str) -> str:
    fd, filename = tempfile.mkstemp(suffix)
    data = base64.b64decode(text)
    path = Path(filename)
    path.write_bytes(data)

    os.close(fd)
    atexit.register(path.unlink)
    return path.as_posix()


def create_image_file_pgf(
    text: str,
    defaults: Path,
    pandoc_path: Path | None = None,
) -> tuple[str, str]:
    doc = Doc(Plain(RawInline(text, format="latex")))
    defaults = create_defaults_for_standalone(defaults)
    fd, filename = tempfile.mkstemp(".pdf")

    convert_text(
        doc,
        output_format="pdf",
        standalone=True,
        extra_args=["--defaults", defaults.as_posix(), "--toc=false", "-o", filename],
        pandoc_path=pandoc_path,
    )

    path = Path(filename)
    data = path.read_bytes()
    text = base64.b64encode(data).decode()

    os.close(fd)
    atexit.register(path.unlink)
    return path.as_posix(), text


def create_defaults_for_standalone(path: Path) -> Path:
    with path.open(encoding="utf8") as f:
        defaults: dict[str, Any] = yaml.safe_load(f)

    variables: dict[str, Any] = defaults.get("variables", {})
    documentclass = variables.get("documentclass")
    variables["documentclass"] = "standalone"
    defaults["variables"] = variables

    if documentclass:
        options: list[str] = variables.get("classoption", [])
        options.append(f"class={documentclass}")
        variables["classoption"] = options

    text = yaml.dump(defaults)

    fd, filename = tempfile.mkstemp(".yaml", dir=path.parent, text=True)
    path = Path(filename)
    path.write_text(text, encoding="utf8")

    os.close(fd)
    atexit.register(path.unlink)
    return path


def create_image_file_svg(xml: str) -> str:  # noqa: ARG001
    raise NotImplementedError

    # file_obj = io.StringIO(image.url)
    # id = image.identifier.replace("fig:", "")
    # write_to = str(root / f"{id}.pdf")
    # cairosvg.svg2pdf(file_obj=file_obj, write_to=write_to)
    # return write_to.replace("\\", "/")
