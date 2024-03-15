from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import nbformat


@dataclass
class Store:
    path: list[Path] = field(default_factory=lambda: [Path(".")])
    notebooks: dict[Path, dict] = field(default_factory=dict, init=False)
    st_mtime: dict[Path, float] = field(default_factory=dict, init=False)
    current_path: Path | None = field(default=None, init=False)

    def insert_path(self, index: int, path: str | Path):
        self.path.insert(index, Path(path))

    def read(self, abs_path: Path):
        with open(abs_path, encoding="utf-8") as f:
            self.notebooks[abs_path] = nbformat.reader.reads(f.read())

        self.st_mtime[abs_path] = abs_path.stat().st_mtime

    def get_notebook(self, path: str | Path | None = None) -> dict:
        if not path:
            if self.current_path is None:
                msg = "Unknown path."
                raise ValueError(msg)

            abs_path = self.current_path

        else:
            for parent in self.path:
                abs_path = (parent / path).absolute()
                if abs_path in self.notebooks or abs_path.exists():
                    break

            else:
                msg = f"Unknown path: {path}"
                raise ValueError(msg)

        if abs_path not in self.notebooks or self.st_mtime[abs_path] < abs_path.stat().st_mtime:
            self.read(abs_path)

        self.current_path = abs_path
        return self.notebooks[abs_path]

    def get_cell(self, id_: str, path: str | Path | None = None) -> dict[str, Any]:
        nb = self.get_notebook(path)
        return get_cell(nb, id_)

    def get_source(self, id_: str, path: str | Path | None = None) -> str:
        nb = self.get_notebook(path)
        return get_source(nb, id_)

    def get_outputs(self, id_: str, path: str | Path | None = None) -> list:
        nb = self.get_notebook(path)
        return get_outputs(nb, id_)

    def get_data(self, id_: str, path: str | Path | None = None) -> dict[str, str]:
        outputs = self.get_outputs(id_, path)
        return get_data_by_id(outputs, id_)

    def get_language(self, path: str | Path | None = None) -> str:
        nb = self.get_notebook(path)
        return get_language(nb)


def set_id(nb: dict):
    for cell in nb["cells"]:
        source: str = cell["source"]
        if source.startswith("# "):
            id_ = source.split()[1]
            if id_[0] == "#":
                cell["metadata"]["id"] = id_[1:]


def get_ids(nb: dict, prefix: str = "") -> list[str]:
    set_id(nb)
    ids: list[str] = []
    for cell in nb["cells"]:
        if id_ := cell["metadata"].get("id"):
            if not isinstance(id_, str) or prefix and not id_.startswith(prefix):
                continue

            ids.append(id_)

    return ids


def get_cell(nb: dict, id_: str) -> dict[str, Any]:
    done = False
    for cell in nb["cells"]:
        if "id" not in cell["metadata"] and not done:
            set_id(nb)
            done = True

        if cell["metadata"].get("id") == id_:
            return cell

    msg = f"Unknown id: {id_}"
    raise ValueError(msg)


def get_source(nb: dict, id_: str) -> str:
    if source := get_cell(nb, id_).get("source", ""):
        source = "\n".join(source.split("\n")[1:])

    return source


def get_outputs(nb: dict, id_: str) -> list:
    return get_cell(nb, id_).get("outputs", [])


def get_language(nb: dict) -> str:
    return nb["metadata"]["kernelspec"]["language"]


def get_data(outputs: list, output_type: str) -> dict[str, str]:
    for output in outputs:
        if output["output_type"] == output_type:
            return output["data"]

    msg = f"No output_type: {output_type}"
    raise ValueError(msg)


def get_display_data(outputs: list) -> dict[str, str]:
    return get_data(outputs, "display_data")


def get_execute_result(outputs: list) -> dict[str, str]:
    return get_data(outputs, "execute_result")


def get_data_by_id(outputs: list, id_: str) -> dict[str, str]:
    if id_.startswith("fig:"):
        try:
            return get_data(outputs, "display_data")
        except ValueError:
            pass

    return get_data(outputs, "execute_result")
