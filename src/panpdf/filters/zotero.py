import json
from collections.abc import Iterator
from dataclasses import dataclass, field

from aiohttp import ClientError, ClientResponse
from panflute import Cite, Doc, Element

from panpdf.core import asyncget
from panpdf.core.filter import Filter


@dataclass
class Zotero(Filter):
    types: type[Element] = Cite
    csl: dict[str, dict] = field(default_factory=dict)

    def action(self, elem: Cite, doc: Doc):
        for key in get_keys(elem):
            if key not in self.csl:
                self.csl[key] = {}

    def finalize(self, doc: Doc):
        if keys := [key for key in self.csl if not self.csl[key]]:
            urls = [get_url(key) for key in keys]
            try:
                csls = asyncget.get(urls, get_csl)
            except ClientError:
                pass  # TODO: warning
            else:
                self.csl.update(dict(zip(keys, csls)))  # noqa: B905
        if csls := [csl for csl in self.csl.values() if csl]:
            doc.metadata["references"] = csls


def get_keys(cite: Cite) -> Iterator[str]:
    for c in cite.citations:
        yield c.id


def get_url(key: str) -> str:
    return f"http://localhost:23119/zotxt/items?betterbibtexkey={key}"


async def get_csl(response: ClientResponse) -> dict:
    if response.status != 200:
        return {}
    text = await response.text()
    return json.loads(text)[0]
