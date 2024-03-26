from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import aiohttp
import pyzotero.zotero
from aiohttp import ClientError, ClientResponse, ClientSession
from panflute import Cite

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from collections.abc import Iterator

    from panflute import Doc


@dataclass(repr=False)
class Zotero(Filter):
    types: ClassVar[type[Cite]] = Cite
    keys: list[str] = field(default_factory=list, init=False)

    def action(self, elem: Cite, doc: Doc) -> None:  # noqa: ARG002
        for citation in elem.citations:
            key = citation.id
            if key not in self.keys:
                self.keys.append(key)

    def finalize(self, doc: Doc) -> None:
        if not self.keys:
            return

        if items := get_items_zotxt(self.keys):
            doc.metadata["references"] = items
            return

        if items is not None:
            return

        if items := get_items_api(self.keys):
            doc.metadata["references"] = items


def get_items_zotxt(keys: list[str]) -> list[dict] | None:
    urls = [get_url_zotxt(key) for key in keys]

    try:
        asyncio.run(gather([urls[0]], get_csl))
    except ClientError:
        return None

    return [ref for ref in asyncio.run(gather(urls, get_csl)) if ref]


def get_url_zotxt(key: str, host: str = "localhost", port: int = 23119) -> str:
    return f"http://{host}:{port}/zotxt/items?betterbibtexkey={key}"


async def get_csl(response: ClientResponse) -> dict:
    if response.status != 200:  # noqa: PLR2004
        return {}

    text = await response.text()
    return json.loads(text)[0]


def get_zotero_api() -> pyzotero.zotero.Zotero | None:
    library_id = os.getenv("ZOTERO_LIBRARY_ID")
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE") or "user"
    api_key = os.getenv("ZOTERO_API_KEY")

    if not library_id or not api_key:
        return None

    return pyzotero.zotero.Zotero(library_id, library_type, api_key)


def get_items_api(
    keys: list[str],
    start: int | None = None,
    limit: int | None = None,
) -> list[dict] | None:
    if not (zot := get_zotero_api()):
        return None

    items = []
    for key, item in iter_items_api(zot, start, limit):
        if key in keys:
            items.append(item)

    return items


def iter_items_api(
    zot: pyzotero.zotero.Zotero,
    start: int | None = None,
    limit: int | None = None,
) -> Iterator[tuple[str, dict]]:
    for item in zot.items(content="csljson", start=start, limit=limit):
        item_ = convert_note(item)  # type:ignore
        if key := item_.get("id"):
            yield key, item_


def convert_note(item: dict):
    if not (note := item.pop("note", None)):
        return item

    for line in note.splitlines():
        if ":" in line:
            name, text = line.split(":", maxsplit=1)
            text = text.strip()
            if name == "Citation Key":
                item["id"] = text
            else:
                item[name.lower().replace(" ", "-")] = text

    return item


# Ref: https://gist.github.com/rhoboro/86629f831934827d832841709abfe715


async def get(session: ClientSession, url: str, coro):
    response = await session.get(url)
    return await coro(response)


async def gather(urls: list[str], coro):
    async with aiohttp.ClientSession() as session:
        tasks = (asyncio.create_task(get(session, url, coro)) for url in urls)
        return await asyncio.gather(*tasks)


# def set_asyncio_event_loop_policy():
#     if not sys.platform.startswith("win"):
#         return

#     import asyncio

#     try:
#         from asyncio import WindowsSelectorEventLoopPolicy
#     except ImportError:
#         pass
#     else:
#         if not isinstance(asyncio.get_event_loop_policy(), WindowsSelectorEventLoopPolicy):
#             asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
