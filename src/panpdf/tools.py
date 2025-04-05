from __future__ import annotations

import asyncio
import atexit
import inspect
import io
import os
import re
import shutil
import tempfile
from asyncio.subprocess import PIPE
from pathlib import Path
from typing import TYPE_CHECKING, Any

import panflute as pf
import yaml
from panflute import Doc
from panflute.io import dump
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

if TYPE_CHECKING:
    from asyncio.streams import StreamReader
    from collections.abc import Callable, Iterable, Iterator

console = Console(log_time=False, log_path=False)

PANDOC_PATH: list[Path] = []


def get_pandoc_path(pandoc_cmd: str = "pandoc") -> Path:
    if PANDOC_PATH:
        return PANDOC_PATH[0]

    if path := shutil.which(pandoc_cmd):
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
            return Path(line.split(":", maxsplit=1)[1].strip())

    raise NotImplementedError


TEMPFILE_PREFIX = "panpdf__"


def create_temp_file(
    text: str | bytes | None,
    *,
    suffix: str | None = None,
    prefix: str = TEMPFILE_PREFIX,
    dir: str | Path | None = None,  # noqa: A002
) -> Path:
    fd, filename = tempfile.mkstemp(suffix, prefix, dir, text=isinstance(text, str))

    path = Path(filename)

    if isinstance(text, str):
        path.write_text(text, encoding="utf8")
    elif text:
        path.write_bytes(text)

    os.close(fd)
    atexit.register(lambda: path.unlink(missing_ok=True))
    return path


def create_temp_dir(
    *,
    suffix: str | None = None,
    prefix: str = TEMPFILE_PREFIX,
    dir: str | Path | None = None,  # noqa: A002
) -> Path:
    dirname = tempfile.mkdtemp(suffix, prefix, dir)
    path = Path(dirname)
    atexit.register(lambda: shutil.rmtree(path))
    return path


def get_file_path(name: Path | str | None, dir: str) -> Path | None:  # noqa: A002
    if not name:
        return None

    if (path := Path(name)).exists():
        return path

    path = Path(f"{name}.yaml")
    if path.exists():
        return path

    data_dir = get_data_dir()

    path = data_dir / dir / name
    if path.exists():
        return path

    path = data_dir / dir / f"{name}.yaml"
    if path.exists():
        return path

    return None


def get_defaults_file_path(defaults: Path | str | None) -> Path | None:
    return get_file_path(defaults, "defaults")


def convert_doc(  # noqa: PLR0913
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
) -> Any:  # noqa: ANN401
    if output_format == "latex":
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

    return progress(
        args,
        f"[green]{description}",
        transient=transient or quiet,
        verbose=verbose,
    )


def progress(
    args: list[str],
    description: str = "",
    *,
    transient: bool = False,
    verbose: bool = False,
) -> int | None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=transient,
    ) as progress:
        task = progress.add_task(description, total=None)

        def stdout(output: str) -> None:
            if TEMPFILE_PREFIX not in output:
                progress.log(f"[green]{output}".rstrip())

        def stderr(output: str) -> None:
            if not verbose and (output.startswith(" ") or TEMPFILE_PREFIX in output):
                return

            color = get_color(output)

            progress.log(f"[{color}]{output}".rstrip())

        coro = run(args, stdout, stderr)

        returncode = asyncio.run(coro)

        description = "[red bold]Fail" if returncode else "[green bold]Done"
        progress.update(task, description=description, total=1)
        progress.advance(task)

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
        return "red"

    if "WARNING" in text or "Warning" in text:
        return "yellow"

    if "LaTeX run number" in text:
        return "green"

    if "INFO" in text:
        return "gray50"

    return "gray70"


def get_metadata_str(doc: Doc, name: str, default: str | None = None) -> str | None:
    if metadata := doc.metadata.get(name):
        return pf.stringify(metadata)

    return default


def add_metadata_str(doc: Doc, name: str, value: str) -> None:
    if metadata := get_metadata_str(doc, name):
        value = f"{metadata}\n{value}"

    doc.metadata[name] = value


def iter_metadata_list(doc: Doc, name: str) -> Iterator[str]:
    if metadata := doc.metadata.get(name):
        for value in metadata:
            yield pf.stringify(value)


def add_metadata_list(doc: Doc, name: str, value: str) -> None:
    if metadata := doc.metadata.get(name):
        metadata.append(value)
    else:
        doc.metadata[name] = [value]


def iter_extra_args_from_metadata(
    doc: Doc,
    resource_path: Iterable[Path | str] = (),
    defaults: Path | str | None = None,
) -> Iterator[str]:
    convert_header(doc, resource_path, defaults)

    names = ["include-in-header", "include-before-body", "include-after-body"]
    for name in names:
        for value in iter_metadata_list(doc, name):
            yield f"--{name}"
            yield value


def resolve_path(path: Path, value: str) -> str:
    return value.replace("${.}", path.parent.as_posix())


def get_defaults(path: Path | str, name: str) -> Any:  # noqa: ANN401
    if not (default_path := get_defaults_file_path(path)):
        return None

    with default_path.open(encoding="utf8") as f:
        defaults = yaml.safe_load(f)

    value = defaults.get(name)

    if isinstance(value, str):
        return resolve_path(default_path, value)

    if isinstance(value, list):
        return [resolve_path(default_path, v) for v in value]

    return value


def search_path(
    path: Path | str,
    resource_path: Iterable[Path | str] = (),
    defaults: Path | str | None = None,
) -> Path:
    if isinstance(path, str):
        path = Path(path)

    if path.exists():
        return path

    resource_path = [Path(p) for p in resource_path]

    if defaults and (paths := get_defaults(defaults, "resource-path")):
        resource_path.extend(Path(p) for p in paths)

    for parent in resource_path:
        if (parent / path).exists():
            return parent / path

    return path


def resolve_image(
    text: str,
    resource_path: Iterable[Path | str] = (),
    defaults: Path | str | None = None,
) -> str:
    if m := re.match(r"^(\\includegraphics.*?)\{(.+?)\}$", text):
        prefix, path = m.groups()
        text = search_path(path, resource_path, defaults).as_posix()
        return f"{prefix}{{{text}}}"

    return text


HEADER = inspect.cleandoc(
    r"""
\usepackage{fancyhdr}
\renewcommand{\headrulewidth}{0pt}
\pagestyle{fancy}
\AtBeginDocument{\addtocontents{toc}{\protect\thispagestyle{fancy}}}
""",
)


def convert_header(
    doc: Doc,
    resource_path: Iterable[Path | str] = (),
    defaults: Path | str | None = None,
) -> None:
    names = ["rhead", "lhead"]
    lines = []
    for name in names:
        if text := get_metadata_str(doc, name):
            doc.metadata.pop(name)
            text = resolve_image(text, resource_path, defaults)
            lines.append(f"\\{name}{{{text}}}")
            if text.startswith("\\includegraphics"):
                path = create_temp_file("\\usepackage{graphicx}", suffix=".tex")
                add_metadata_list(doc, "include-in-header", path.as_posix())

    if lines:
        header = "\n".join(lines)
        header = f"{HEADER}\n{header}"
        path = create_temp_file(header, suffix=".tex")
        add_metadata_list(doc, "include-in-header", path.as_posix())
