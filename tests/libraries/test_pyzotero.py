import os

from pyzotero import zotero as z


def test_pyzotero():
    library_id = os.getenv("ZOTERO_LIBRARY_ID")
    api_key = os.getenv("ZOTERO_API_KEY")
    zot = z.Zotero(library_id, "user", api_key)
    items_data = zot.items()
    assert items_data
