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

    print(items)
    assert 0
    # assert len(refs) == 1
    # assert isinstance(refs[0], dict)
    # for x in refs[0].items():
    #     print(x)
    # assert 0


def test_get_items_api():
    from panpdf.filters.zotero import get_items_api

    keys = ["panpdf", "panflute", "x"]
    items = get_items_api(keys)
    print(items)
    assert 0
    # for x in refs.entries[0].items():
    #     print(x)
    # # for x in refs[0]["data"].items():
    # #     print(x)
    # import bibtexparser

    # print(bibtexparser.dumps(refs))

    # assert 0


# def test_get_csl():
#     import asyncio

#     from panpdf.filters.zotero import gather, get_csl, get_url_zotxt

#     url = get_url_zotxt("panflute")
#     res = asyncio.run(gather([url], get_csl))
#     print(res)
#     assert 0
