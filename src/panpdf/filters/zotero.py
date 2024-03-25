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

        # if items := get_items_api(self.keys):

        if items := get_items_zotxt(self.keys):
            doc.metadata["references"] = items
            return

        if items is not None:
            return

        # if keys := [key for key in self.csl if not self.csl[key]]:
        #     urls = [get_url_zotxt(key, self.host, self.port) for key in keys]
        #     try:
        #         csls = asyncio.run(gather(urls, get_csl))
        #     except ClientError:
        #         pass
        #     else:
        #         self.csl.update(dict(zip(keys, csls, strict=True)))

        # if csls := [csl for csl in self.csl.values() if csl]:
        #     doc.metadata["references"] = csls


def get_items(keys: list[str]) -> list[dict]:
    refs = get_items_zotxt(keys)
    if refs is not None:
        return refs

    return []


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


def get_items_api(keys: list[str]) -> list[dict] | None:
    library_id = os.getenv("ZOTERO_LIBRARY_ID")
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE") or "user"
    api_key = os.getenv("ZOTERO_API_KEY")

    if not library_id or not api_key:
        return None

    zot = pyzotero.zotero.Zotero(library_id, library_type, api_key)
    return zot.items(format="bibtex")

    items = []
    for item in zot.items():
        if (item_ := convert_item_api(item)) and item_["id"] in keys:  # type: ignore
            items.append(item)  # noqa: PERF401

    return items


def convert_item_api(ref: dict) -> dict | None:
    if key := get_key(ref):
        ref["id"] = key
        return ref

    return None


def get_key(ref: dict) -> str | None:
    if not (extra := ref.get("extra")):
        return None

    for line in extra.splitlines():
        if ":" in line:
            name, text = line.split(":", maxsplit=1)
            if name == "Citation Key":
                return text.strip()

    return None


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
