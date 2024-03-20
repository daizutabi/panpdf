from itertools import chain

import panflute as pf
from panflute import Cite, Para

from panpdf.filters.zotero import Zotero, iter_keys


def test_zotero():
    zotero = Zotero()
    zotero.run("a d e [@zotero] [@XXX]")
    assert "zotero" in zotero.csl
    assert "XXX" in zotero.csl


def test_get_keys():
    elems = pf.convert_text("a b [@key1], [@key2; @key3; @key4] @key5")
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, Para)
    keys_ = [iter_keys(c) for c in para.content if isinstance(c, Cite)]
    keys = list(chain.from_iterable(keys_))  # type:ignore
    for i in range(1, 6):
        assert f"key{i}" in keys


# def test_get_csl():
#     import asyncio

#     from panpdf.filters.zotero import gather, get_csl, get_url

#     url = get_url("panflute")
#     print(url)
#     assert 0
#     res = asyncio.run(gather([url], get_csl))
#     print(res)
#     assert 0
