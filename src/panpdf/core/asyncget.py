"""Ref: https://gist.github.com/rhoboro/86629f831934827d832841709abfe715"""

import asyncio

import aiohttp
from aiohttp import ClientSession


async def _get(session: ClientSession, url: str, coro):
    response = await session.get(url)
    return await coro(response)


async def _gather(urls: list[str], coro):
    async with aiohttp.ClientSession() as session:
        tasks = (asyncio.create_task(_get(session, url, coro)) for url in urls)
        return await asyncio.gather(*tasks)


def get(urls: list[str], coro):
    """HTTPリソースを並列に取得し、任意の処理を行う。

    Args:
        urls (list of str): URLの一覧。
        coro: aiohttp.ClientResponseを引数に取るコルーチン。

    Returns:
        coroの戻り値のリスト。urlsと同順で返す。
    """
    return asyncio.run(_gather(urls, coro))
