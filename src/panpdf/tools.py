from __future__ import annotations

import asyncio
import atexit
import io
import os
import shutil
import tempfile
from asyncio.subprocess import PIPE
from pathlib import Path
from typing import TYPE_CHECKING

import panflute as pf
from panflute import Doc
from panflute.io import dump
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

if TYPE_CHECKING:
    from asyncio.streams import StreamReader
    from collections.abc import Callable

console = Console()


def get_metadata(doc: Doc, name: str, default: str | None = None) -> str | None:
    if metadata := doc.metadata.content.get(name):
        return pf.stringify(metadata)

    return default


def add_metadata(doc: Doc, name: str, value: str) -> None:
    if metadata := get_metadata(doc, name):
        value = f"{metadata}\n{value}"

    doc.metadata[name] = value


PANDOC_PATH: list[Path] = []


def get_pandoc_path() -> Path:
    if PANDOC_PATH:
        return PANDOC_PATH[0]

    if path := shutil.which("pandoc"):
        PANDOC_PATH.append(Path(path))
        return PANDOC_PATH[0]

    msg = "Path to pandoc executable does not exists"
    raise OSError(msg)


def get_pandoc_version(pandoc_path: Path | None = None) -> str:
    output: str = pf.run_pandoc(args=["--version"], pandoc_path=pandoc_path)
    return output.splitlines()[0].split(" ")[1]


def get_data_dir(pandoc_path: Path | None = None) -> Path:
    output: str = pf.run_pandoc(args=["--version"], pandoc_path=pandoc_path)

    for line in output.splitlines():
        if line.startswith("User data directory:"):
            return Path(line.split(":")[1].strip())

    raise NotImplementedError


def get_defaults_file_path(defaults: Path | None) -> Path | None:
    if not defaults:
        return None

    if defaults.exists():
        return defaults

    path = Path(f"{defaults}.yaml")
    if path.exists():
        return path

    data_dir = get_data_dir()

    path = data_dir / "defaults" / defaults
    if path.exists():
        return path

    path = data_dir / "defaults" / f"{defaults}.yaml"
    if path.exists():
        return path

    return None


def create_temp_file(
    text: str | bytes,
    suffix: str | None = None,
    dir: str | Path | None = None,  # noqa: A002
) -> Path:
    fd, filename = tempfile.mkstemp(suffix=suffix, dir=dir, text=isinstance(text, str))

    path = Path(filename)

    if isinstance(text, str):
        path.write_text(text, encoding="utf8")
    else:
        path.write_bytes(text)

    os.close(fd)
    atexit.register(path.unlink)
    return path


def convert_doc(
    doc: Doc,
    *,
    output_format: str = "latex",
    standalone: bool = False,
    extra_args: list[str] | None = None,
    pandoc_path: Path | None = None,
    description: str = "",
    verbose: bool = False,
    quiet: bool = False,
    transient: bool = False,
):
    if output_format == "latex":
        if not standalone:
            extra_args = []

        return pf.convert_text(
            doc,
            input_format="panflute",
            output_format="latex",
            standalone=standalone,
            extra_args=extra_args,
            pandoc_path=pandoc_path,
        )

    with io.StringIO() as f:
        dump(doc, f)
        text = f.getvalue()

    fd, filename = tempfile.mkstemp(".json", text=True)
    path = Path(filename)
    path.write_text(text, encoding="utf8")

    os.close(fd)
    atexit.register(path.unlink)

    extra_args = extra_args[:] if extra_args else []

    extra_args.extend(["--from", "json", "--to", "pdf", "--standalone", "--verbose"])

    if quiet:
        extra_args.append("--quiet")

    if not pandoc_path:
        pandoc_path = get_pandoc_path()

    args = [str(pandoc_path), filename, *extra_args]

    if not description:
        output = extra_args[extra_args.index("--output") + 1]
        description = f"Producing {output}"

    return progress(args, f"[green]{description}", transient=transient or quiet, verbose=verbose)


def progress(
    args: list[str],
    description: str = "",
    *,
    transient: bool = False,
    verbose: bool = False,
) -> int | None:
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=transient,
    ) as progress:
        task = progress.add_task(description, total=None)

        def stdout(output: str) -> None:
            progress.log(f"[green]{output}".rstrip())

        def stderr(output: str) -> None:
            if not verbose and output.startswith(" "):
                return

            color = get_color(output)

            progress.log(f"[{color}]{output}".rstrip())

        coro = run(args, stdout, stderr)

        returncode = asyncio.run(coro)

        description = "[red bold]Fail" if returncode else "[green bold]Done"
        progress.update(task, description=description, total=0)

        return returncode


async def run(
    args: list[str],
    stdout: Callable[[str], None],
    stderr: Callable[[str], None],
) -> int | None:
    process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)

    coros = log(process.stdout, stdout), log(process.stderr, stderr)  # type:ignore
    await asyncio.gather(*coros)

    await process.communicate()

    return process.returncode


async def log(reader: StreamReader, write: Callable[[str], None]) -> None:
    while True:
        if reader.at_eof():
            break

        if out := await reader.readline():
            write(out.decode())


def get_color(text: str) -> str:
    if "ERROR" in text or "Error" in text:
        return "red bold"

    if "WARNING" in text or "Warning" in text:
        return "red"

    if "INFO" in text:
        return "yellow"

    return "gray70"
