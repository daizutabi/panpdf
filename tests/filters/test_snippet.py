from __future__ import annotations

from typing import TYPE_CHECKING

from panflute import CodeBlock, Doc, Figure, Image, Plain, Str

if TYPE_CHECKING:
    from nbstore import Store


def test_action_none(store: Store):
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    figure = Figure()
    elems = snippet.action(figure, Doc())
    assert elems is figure


def test_action_not_plain(store: Store):
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    figure = Figure(CodeBlock("a"))
    elems = snippet.action(figure, Doc())
    assert elems is figure


def test_action_not_image(store: Store):
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    figure = Figure(Plain(Str("a")))
    elems = snippet.action(figure, Doc())
    assert elems is figure


def test_action_not_file(store: Store):
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    figure = Figure(Plain(Image(Str("a"), url="a")))
    elems = snippet.action(figure, Doc())
    assert elems is figure


def test_action_not_class(store: Store):
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    url = "tests/examples/a.txt"
    figure = Figure(Plain(Image(Str("a"), url=url)))
    elems = snippet.action(figure, Doc())
    assert elems is figure


def test_action_source():
    from panpdf.filters.snippet import Snippet

    snippet = Snippet()
    url = "tests/examples/a.txt"
    attrs = {"title": "abc.txt"}
    image = Image(Str("a"), url=url, classes=["source", "output"], attributes=attrs)
    figure = Figure(Plain(image))
    code_block = snippet.action(figure, Doc())
    assert isinstance(code_block, CodeBlock)
    assert code_block.text == "text αβγ"
    assert code_block.classes == ["output"]
    assert code_block.attributes == attrs
