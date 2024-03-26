import panflute as pf
from panflute import Cite, Doc, Para


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


def test_zotero():
    from panpdf.filters.zotero import Zotero

    doc = pf.convert_text("[@panflute;@panpdf]", standalone=True)
    assert isinstance(doc, Doc)

    doc = Zotero().run(doc)

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
