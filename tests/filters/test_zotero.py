import os

import panflute as pf
import pytest
from panflute import Cite, Doc, Para


@pytest.fixture(autouse=True)
def _clear_csl_path():
    from panpdf.filters.zotero import CSL_PATH

    CSL_PATH.unlink(missing_ok=True)
    yield
    CSL_PATH.unlink(missing_ok=True)


def test_keys():
    from panpdf.filters.zotero import Zotero

    zotero = Zotero()

    elems = pf.convert_text("[@key1; @key2; @key3]")
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    cite = para.content[0]
    assert isinstance(cite, Cite)
    zotero.action(cite, Doc())
    assert zotero.keys == ["key1", "key2", "key3"]
    zotero.action(cite, Doc())
    assert zotero.keys == ["key1", "key2", "key3"]


def test_get_items_zotxt():
    from panpdf.filters.zotero import get_items_zotxt

    keys = ["panpdf", "panflute", "x"]
    items = get_items_zotxt(keys)

    if items is None:
        return

    assert len(items) == 2
    assert isinstance(items[0], dict)


def test_get_items_api():
    from panpdf.filters.zotero import get_items_api

    keys = ["panpdf", "panflute", "x"]
    items = get_items_api(keys)

    assert items
    assert len(items) == 2
    assert isinstance(items[0], dict)


def test_convert_note():
    from panpdf.filters.zotero import convert_note

    item = {}
    assert convert_note(item) is item

    item = {"note": "Citation Key: abc\nA B: a"}
    item = convert_note(item)
    assert item["id"] == "abc"
    assert item["a-b"] == "a"


def test_invalid_env():
    from panpdf.filters.zotero import get_items_api, get_zotero_api

    name = "ZOTERO_API_KEY"
    if not (env := os.getenv(name)):
        return

    os.environ[name] = ""
    assert not get_zotero_api()
    assert get_items_api([]) is None
    os.environ[name] = env


def test_zotero_csl_path():
    from panpdf.filters.zotero import (
        CSL_PATH,
        get_items,
        get_items_api,
        get_items_zotxt,
    )

    keys = ["panflute", "panpdf"]
    get_items(keys)
    assert CSL_PATH.exists()

    items = get_items_zotxt(keys) or get_items_api(keys)
    csl = get_items(keys)
    assert csl == items

    csl = CSL_PATH.read_text(encoding="utf-8")
    assert "generator あα" in csl


def test_zotero():
    from panpdf.filters.zotero import Zotero

    doc = pf.convert_text("[@panflute;@panpdf]", standalone=True)
    assert isinstance(doc, Doc)

    zotero = Zotero()
    doc = zotero.run(doc)
    assert zotero.keys == ["panflute", "panpdf"]
    assert "references" in doc.metadata

    tex = pf.convert_text(
        doc,
        input_format="panflute",
        output_format="latex",
        extra_args=["--citeproc", "--csl", "https://www.zotero.org/styles/ieee"],
    )
    assert isinstance(tex, str)
    assert "{[}1{]}, {[}2{]}\n\n" in tex
    assert "\\CSLLeftMargin{{[}1{]} }%" in tex
    assert "\\url{https://github.com/daizutabi/panpdf}}" in tex


def test_zotero_nokey():
    from panpdf.filters.zotero import Zotero

    doc = Doc()
    Zotero().finalize(doc)
    assert not doc.metadata
