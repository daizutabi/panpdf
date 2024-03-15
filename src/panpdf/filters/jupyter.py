from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from panflute import Image

from panpdf.filters.filter import Filter
from panpdf.stores import Store

if TYPE_CHECKING:
    from panflute import Doc


@dataclass
class Jupyter(Filter):
    types: type[Image] = Image
    store: Store = field(default_factory=Store)

    def action(self, image: Image, doc: Doc) -> Image:  # noqa: ARG002
        url = image.url
        id_ = image.identifier
        if id_ and (not url or url.endswith(".ipynb")):
            try:
                data = self.store.get_data(id_, url)
            except ValueError:
                msg = f"[panpdf] Unknown url or id: url='{url}' id='{id_}'"
                raise ValueError(msg) from None

            if data:
                return convert_image(data, image)

        return image


def convert_image(data: dict[str, str], image: Image) -> Image:
    mimes = list(data.keys())
    if "application/pdf" in mimes:
        return convert_image_pdf(data, image)

    if "image/svg+xml" in mimes:
        return convert_image_svg(data, image)

    if "text/plain" in mimes:
        return convert_image_pgf(data, image)

    return convert_image_base64(data, image)


def convert_image_base64(data: dict[str, str], image: Image) -> Image:
    for mime, text in data.items():
        if mime.startswith("image/"):
            image.url = f"data:{mime};base64,{text}"
            image.classes.append("panpdf-base64")
            return image

    return image


def convert_image_pdf(data: dict[str, str], image: Image) -> Image:
    image.url = data["application/pdf"]
    image.classes.append("panpdf-pdf")
    return image


def convert_image_svg(data: dict[str, str], image: Image) -> Image:
    image.url = data["image/svg+xml"]
    image.classes.append("panpdf-svg")
    return image


def convert_image_pgf(data: dict[str, str], image: Image) -> Image:
    if "\\" not in (text := data["text/plain"]):
        return convert_image_base64(data, image)

    image.url = text.strip()
    image.classes.append("panpdf-pgf")
    return image
