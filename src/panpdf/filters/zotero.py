from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import aiohttp
from aiohttp import ClientError, ClientResponse, ClientSession
from panflute import Cite

from panpdf.filters.filter import Filter

if TYPE_CHECKING:
    from collections.abc import Iterator

    from panflute import Doc


@dataclass(repr=False)
class Zotero(Filter):
    types: ClassVar[type[Cite]] = Cite
    csl: dict[str, dict] = field(default_factory=dict, init=False)
    host: str = "localhost"
    port: int = 23119

    def action(self, elem: Cite, doc: Doc):  # noqa: ARG002
        for key in iter_keys(elem):
            if key not in self.csl:
                self.csl[key] = {}

    def finalize(self, doc: Doc):
        if keys := [key for key in self.csl if not self.csl[key]]:
            urls = [get_url(key, self.host, self.port) for key in keys]
            try:
                csls = asyncio.run(gather(urls, get_csl))
            except ClientError:
                pass
            else:
                self.csl.update(dict(zip(keys, csls, strict=True)))

        if csls := [csl for csl in self.csl.values() if csl]:
            doc.metadata["references"] = csls


def iter_keys(cite: Cite) -> Iterator[str]:
    for c in cite.citations:
        yield c.id


def get_url(key: str, host: str, port: int) -> str:
    return f"http://{host}:{port}/zotxt/items?betterbibtexkey={key}"


async def get_csl(response: ClientResponse) -> dict:
    if response.status != 200:  # noqa: PLR2004
        return {}

    text = await response.text()
    return json.loads(text)[0]


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
