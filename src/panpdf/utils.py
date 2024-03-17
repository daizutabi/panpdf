from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import panflute as pf
from panflute import Doc

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


def set_asyncio_event_loop_policy():
    if not sys.platform.startswith("win"):
        return

    import asyncio

    try:
        from asyncio import WindowsSelectorEventLoopPolicy
    except ImportError:
        pass
    else:
        if not isinstance(asyncio.get_event_loop_policy(), WindowsSelectorEventLoopPolicy):
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def collect(paths: Iterable[Path], suffixes: Iterable[str] = (".md",)) -> Iterator[Path]:
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

    it = (Path(path).read_text(encoding="utf8") for path in paths)
    return "\n\n".join(it)


def get_metadata(doc: Doc, name: str, default: str | None = None) -> str | None:
    if title := doc.metadata.content.get(name):
        return pf.stringify(title)

    return default
