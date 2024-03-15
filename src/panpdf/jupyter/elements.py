from __future__ import annotations

from typing import TYPE_CHECKING

from panflute import CodeBlock, Image

if TYPE_CHECKING:
    from panflute import Math, Table


def convert(
    data: str | dict[str, str], elem: Image | Math, language: str = "python"
) -> Image | Math | Table | CodeBlock:
    if isinstance(elem, Image):
        if isinstance(data, str):
            return convert_image_to_code_block(data, elem, language)

        return convert_image(data, elem)

    # if isinstance(data, dict):
    #     return convert_math(data, elem)

    msg = "Unknown parameters"
    raise ValueError(msg)


def convert_image_to_code_block(source: str, image: Image, language: str = "python") -> CodeBlock:
    identifier = image.identifier
    return CodeBlock(source, identifier, classes=[language])


def convert_image_base64(data: dict[str, str], image: Image) -> Image:
    for mime, text in data.items():
        if mime.startswith("image/"):
            image.url = f"data:{mime};base64,{text}"
            image.classes += ["panpdf-base64"]
            return image

    return image


def convert_image_pdf(data: dict[str, str], image: Image) -> Image:
    image.url = data["application/pdf"]
    image.classes += ["panpdf-pdf"]
    return image


def convert_image_svg(data: dict[str, str], image: Image) -> Image:
    image.url = data["image/svg+xml"]
    image.classes += ["panpdf-svg"]
    return image


def convert_image_pgf(data: dict[str, str], image: Image) -> Image:
    if "\\" not in (text := data["text/plain"]):
        return convert_image_base64(data, image)

    image.url = text.strip()
    image.classes += ["panpdf-pgf"]
    return image


def convert_image(data: dict[str, str], image: Image) -> Image:
    match data:
        case "application/pdf":
            return convert_image_pdf(data, image)

        case "image/svg+xml":
            return convert_image_svg(data, image)

        case "text/plain":
            return convert_image_pgf(data, image)

        case _:
            return convert_image_base64(data, image)


# TABLE_PATTERN = re.compile(r".*?(<table.+?</table>).*", re.DOTALL)


# def convert_image_to_table(data: dict[str, str], image: Image) -> Image | Table:
#     if not (m := TABLE_PATTERN.match(data["text/html"])):
#         return image

#     text = m.group(1)
#     text = re.sub(r"(<p>.*?</p>)", "", text)  # for DataFrames.jl
#     table: Table = pf.convert_text(text, input_format="html")[0]  # type: ignore

#     if caption := image.content:
#         table.caption = pf.Caption(pf.Plain(*caption))

#     table.identifier = image.identifier
#     table.classes = image.classes
#     table.attributes = image.attributes
#     set_table_head(table)
#     return table


# def set_table_head(table: Table):
#     cells = []
#     head = table.head

#     for j in range(len(head.content[0].content)):  # type: ignore
#         for i in range(len(head.content)):
#             cell = head.content[i].content[j]  # type: ignore
#             if cell.content:
#                 cells.append(cell)
#                 if len(cells) > j + 1:
#                     return
#                 break
#         else:
#             return

#     row = pf.TableRow(*cells)
#     head = pf.TableHead(row)
#     table.head = head


# def convert_math(data: dict[str, str], math: Math) -> Math:
#     if "text/latex" not in data:
#         return math

#     text = data["text/latex"].strip()[1:-1].replace("\\displaystyle ", "")
#     text = text.replace("\\begin{equation*}", "").replace("\\end{equation*}", "")
#     math.text = text
#     return math
