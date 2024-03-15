from itertools import chain

import panflute as pf

from panpdf.filters.zotero import Zotero, get_keys


def test_zotero():
    zotero = Zotero()
    zotero.run("a d e [@zotero] [@XXX]")
    assert "zotero" in zotero.csl
    assert "XXX" in zotero.csl


def test_get_keys():
    elems = pf.convert_text("a b [@key1], [@key2; @key3; @key4] @key5")
    assert isinstance(elems, list)
    para = elems[0]
    assert isinstance(para, pf.Para)
    keys_ = [get_keys(c) for c in para.content if isinstance(c, pf.Cite)]
    keys = list(chain.from_iterable(keys_))  # type:ignore
    for i in range(1, 6):
        assert f"key{i}" in keys
