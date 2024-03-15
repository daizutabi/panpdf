import os
import sys
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path

import panflute as pf
from panflute import Code, Element, Para, SoftBreak, Space


def set_asyncio_event_loop_policy():
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        import asyncio

        try:
            from asyncio import WindowsSelectorEventLoopPolicy
        except ImportError:
            pass
        else:
            if not isinstance(asyncio.get_event_loop_policy(), WindowsSelectorEventLoopPolicy):
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def attribute_scanner(elem: Element) -> Generator[tuple[Element, bool], None, None]:
    in_attr = False
    for e in elem.content:
        if in_attr:
            yield e, True
            if isinstance(e, pf.Str) and e.text.endswith("}"):
                in_attr = False
        elif isinstance(e, pf.Str) and e.text.startswith("{#"):
            yield e, True
            in_attr = True
        else:
            yield e, False


def strip_content(content: list[Element]) -> Generator[Element, None, None]:
    spaces = [Space(), SoftBreak()]
    prev = None
    for i, e in enumerate(content):
        if prev is None:
            if e in spaces:
                continue
            else:
                prev = e
        elif e in spaces and prev in spaces:
            continue
        else:
            yield prev
            if i == len(content) - 1 and e not in spaces:
                yield e
            prev = e


def split_attribute(elem: Element) -> tuple[Element, str]:
    content: list[Element] = []
    attr: list[Element] = []
    for e, i in attribute_scanner(elem):
        if i:
            attr.append(e)
        else:
            content.append(e)
    content = list(strip_content(content))
    return type(elem)(*content), pf.stringify(pf.Plain(*attr))


def set_attributes(elem: Element, attr: Element) -> Element | None:
    keys = ["identifier", "classes", "attributes"]
    if any(getattr(elem, key, None) for key in keys):
        return None
    rest, text = split_attribute(attr)
    para: Para = pf.convert_text(f"`__panpdf__`{text}")[0]  # type: ignore
    code: Code = para.content[0]  # type: ignore
    for key in keys:
        setattr(elem, key, getattr(code, key))
    return rest


def collect(paths: Path | Iterable[Path], suffixes: str | Iterable[str] = ".md") -> Iterator[Path]:
    if isinstance(paths, Path):
        paths = [paths]
    if isinstance(suffixes, str):
        suffixes = [suffixes]

    for path in paths:
        if path.is_dir():
            for dirpath, _dirnames, filenames in os.walk(path):
                for file in filenames:
                    path_ = Path(dirpath) / file
                    if path_.suffix in suffixes:
                        yield path_
        elif path.suffix in suffixes:
            yield path


def get_format(path: str | Path, default: str | None = None) -> str:
    if isinstance(path, str):
        path = Path(path)

    if path.suffix == ".tex":
        return "latex"

    if path.suffix == ".pdf":
        return "pdf"

    if default:
        return default

    msg = "Supported format: 'latex' or 'pdf'."
    raise ValueError(msg)


def join_files(paths: Iterable[str | Path] | str | Path):
    if isinstance(paths, Path | str):
        paths = [paths]
    gen = (Path(path).read_text(encoding="utf8") for path in paths)
    return "\n\n".join(gen)
