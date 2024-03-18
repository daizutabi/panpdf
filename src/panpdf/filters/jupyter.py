from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from panflute import Image

from panpdf.filters.filter import Filter
from panpdf.stores import Store

if TYPE_CHECKING:
    from collections.abc import Callable

    from panflute import Doc


@dataclass(repr=False)
class Jupyter(Filter):
    types: ClassVar[type[Image]] = Image
    store: Store = field(default_factory=Store)
    convert: Callable[[dict[str, str], Image], Image] | None = None

    def action(self, image: Image, doc: Doc) -> Image:  # noqa: ARG002
        url = image.url
        identifier = image.identifier
        if identifier and (not url or url.endswith(".ipynb")):
            try:
                data = self.store.get_data(url, identifier)
            except ValueError:
                msg = f"[panpdf] Unknown url or id: url='{url}' id='{identifier}'"
                raise ValueError(msg) from None

            if data and self.convert:
                return self.convert(data, image)

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


# def create_image_file_base64(image: Image, root: Path) -> str:
#     ext = image.url.split("/")[1].split(";")[0]
#     text = image.url[image.url.index("base64,") + 7 :]
#     id_ = image.identifier.replace("fig:", "")
#     path = root / f"{id_}.{ext}"
#     data = base64.b64decode(text)
#     path.write_bytes(data)
#     return path.as_posix()


# def create_image_file_pdf(image: Image, root: Path) -> str:
#     id_ = image.identifier.replace("fig:", "")
#     path = root / f"{id_}.pdf"
#     data = base64.b64decode(image.url)
#     path.write_bytes(data)
#     return path.as_posix()


# def create_image_file_svg(image: Image, root: Path) -> str:  # noqa: ARG001
#     raise NotImplementedError
#     # file_obj = io.StringIO(image.url)
#     # id = image.identifier.replace("fig:", "")
#     # write_to = str(root / f"{id}.pdf")
#     # cairosvg.svg2pdf(file_obj=file_obj, write_to=write_to)
#     # return write_to.replace("\\", "/")
