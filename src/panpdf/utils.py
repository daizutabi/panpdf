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
