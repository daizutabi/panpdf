from __future__ import annotations

from typing import TYPE_CHECKING

import panflute as pf
import pytest
from panflute import CodeBlock, Doc, Figure, Plain

if TYPE_CHECKING:
    from nbstore import Store


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
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    code_block = cell.get_code_block("cell.ipynb", "fig:source")
    assert code_block.text.startswith("fig, ax = plt.subplots")
    assert code_block.classes == ["python"]


def test_get_code_block_unknown(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    with pytest.raises(ValueError):
        cell.get_code_block("cell.ipynb", "fig:invalid")


def test_action_source(store: Store):
    from panpdf.filters.cell import Cell

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
    from panpdf.filters.cell import Cell

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


def test_action_none(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    figure = Figure()
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_action_not_plain(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    figure = Figure(CodeBlock("a"))
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_action_cell_not_image(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    figure = Figure(pf.Plain(pf.Str("a")))
    elems = cell.action(figure, Doc())
    assert elems is figure


def test_stdout(store: Store):
    data = store.get_data("cell.ipynb", "text:stdout")
    assert len(data) == 1
    assert data["text/plain"] == "'stdout'"


def test_print(store: Store):
    data = store.get_stream("cell.ipynb", "text:print")
    assert data == "print\n"


def test_both(store: Store):
    data = store.get_stream("cell.ipynb", "text:both")
    assert data == "print\n"
    data = store.get_data("cell.ipynb", "text:both")
    assert len(data) == 1
    assert data["text/plain"] == "'hello'"


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


def test_action_text_stdout(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    text = "![source](cell.ipynb){#text:stdout .cell}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 2
    code_block = elems[1]
    assert isinstance(code_block, CodeBlock)
    assert code_block.text == "'stdout'"
    assert code_block.classes == ["output"]


def test_action_text_print(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    text = "![source](cell.ipynb){#text:print .output}"
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
    assert code_block.text == "print"
    assert code_block.classes == ["output"]


def test_action_text_both(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    text = "![source](cell.ipynb){#text:both .cell}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 2
    code_block = elems[1]
    assert isinstance(code_block, CodeBlock)
    assert code_block.text == "print\n'hello'"
    assert code_block.classes == ["output"]


def test_action_text_polars(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    text = "![source](cell.ipynb){#text:polars .cell}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 2
    code_block = elems[1]
    assert isinstance(code_block, CodeBlock)
    assert "shape: (3, 2)" in code_block.text
    assert "│ a   │ b   │" in code_block.text
    assert code_block.classes == ["output"]


def test_action_text_pandas(store: Store):
    from panpdf.filters.cell import Cell

    cell = Cell(store=store)
    text = "![source](cell.ipynb){#text:pandas .output .html}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    elems = cell.action(figure, Doc())
    assert isinstance(elems, list)
    assert len(elems) == 1
    assert isinstance(elems[0], pf.Div)


def test_figure_image():
    text = "![caption](a.png){#fig:a}"
    list_ = pf.convert_text(text)
    assert isinstance(list_, list)
    assert len(list_) == 1
    figure = list_[0]
    assert isinstance(figure, Figure)
    tex = pf.convert_text(figure, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\begin{figure}" in tex

    plain = figure.content[0]
    assert isinstance(plain, Plain)
    tex = pf.convert_text(plain, input_format="panflute", output_format="latex")
    assert isinstance(tex, str)
    assert "\\begin{figure}" not in tex
