from __future__ import annotations

from typing import TYPE_CHECKING

import panflute as pf
import pytest
from panflute import CodeBlock, Doc, Figure

from panpdf.filters.cell import Cell

if TYPE_CHECKING:
    from panpdf.stores import Store


def test_source(store: Store):
    source = store.get_source("cell.ipynb", "fig:source")
    assert source.startswith("fig, ax = plt.subplots")


def test_language(store: Store):
    lang = store.get_language("cell.ipynb")
    assert lang == "python"


def test_code_block():
    text = "```python\nprint('a')\na = 1\n```"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    code = list_[0]
    assert isinstance(code, CodeBlock)
    assert code == CodeBlock("print('a')\na = 1", classes=["python"])


def test_get_code_block(store: Store):
    cell = Cell(store=store)
    code_block = cell.get_code_block("cell.ipynb", "fig:source")
    assert code_block.text.startswith("fig, ax = plt.subplots")
    assert code_block.classes == ["python"]


def test_get_code_block_unknown(store: Store):
    cell = Cell(store=store)
    with pytest.raises(ValueError):
        cell.get_code_block("cell.ipynb", "fig:invalid")


def test_action_source(store: Store):
    cell = Cell(store=store)
    text = "![source](cell.ipynb){#fig:source .source}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 1
    code_block = elems[0]
    assert isinstance(code_block, CodeBlock)
    assert code_block.text.startswith("fig, ax = plt.subplots")
    assert code_block.classes == ["python"]


def test_action_cell(store: Store):
    cell = Cell(store=store)
    text = "![source](cell.ipynb){#fig:source .cell}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 2
    code_block = elems[0]
    assert isinstance(code_block, CodeBlock)
    assert code_block.text.startswith("fig, ax = plt.subplots")
    assert code_block.classes == ["python"]
    assert elems[1] is figure


def test_action_cell_none(store: Store):
    cell = Cell(store=store)
    figure = Figure()
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_action_cell_not_plain(store: Store):
    cell = Cell(store=store)
    figure = Figure(CodeBlock("a"))
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_action_cell_not_image(store: Store):
    cell = Cell(store=store)
    figure = Figure(pf.Plain(pf.Str("a")))
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_stdout(store: Store):
    data = store.get_data("cell.ipynb", "text:stdout")
    assert len(data) == 1
    assert data["text/plain"] == "'stdout'"


def test_print(store: Store):
    data = store.get_data("cell.ipynb", "text:print")
    assert len(data) == 1
    assert data["text/plain"] == "print\n"


def test_pandas(store: Store):
    data = store.get_data("cell.ipynb", "text:pandas")
    assert len(data) == 2
    assert "a  b\n0  1  4" in data["text/plain"]
    assert "<div>\n<style scoped>\n" in data["text/html"]


def test_polars(store: Store):
    data = store.get_data("cell.ipynb", "text:polars")
    assert len(data) == 2
    assert "shape: (3, 2)\n┌─────┬─────┐\n" in data["text/plain"]
    assert "<div><style>\n" in data["text/html"]


def test_convert_text_pandas(store: Store):
    data = store.get_data("cell.ipynb", "text:pandas")
    html = data["text/html"]
    list_ = pf.convert_text(html, input_format="html")
    assert isinstance(list_, list)
    assert len(list_) == 1


def test_convert_text_polars(store: Store):
    data = store.get_data("cell.ipynb", "text:polars")
    html = data["text/html"]
    list_ = pf.convert_text(html, input_format="html")
    assert isinstance(list_, list)
    assert len(list_) == 1
