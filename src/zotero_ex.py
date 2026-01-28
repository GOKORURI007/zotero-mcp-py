import json
from typing import Literal

import httpx
from pyzotero import errors as ze, Zotero
from pyzotero._utils import build_url, get_backoff_duration, token

from src.models import AddByIDPayload


class ZoteroEx(Zotero):
    """
    Local only Zotero API client
    extend from pyzotero.Zotero
    """

    def __init__(
        self,
        library_id: str = '0',
        library_type: Literal['user', 'group'] = 'user',
        api_key=None,
        preserve_json_order: bool = False,
        locale: str = 'en-US',
        local: bool = True,
        client: httpx.Client = None,
    ):
        super().__init__(
            library_id,
            library_type,
            api_key,
            preserve_json_order,
            locale,
            local,
            client
        )

    def add_items_by_identifier(
        self,
        identifier: str,
        collection_key: str,
        last_modified=None
    ):
        headers = {"Zotero-Write-Token": token(), "Content-Type": "application/json"}
        if last_modified is not None:
            headers["If-Unmodified-Since-Version"] = str(last_modified)
        self._check_backoff()

        payload = AddByIDPayload(
            identifier=identifier,
            collectionKey=collection_key
        ).model_dump_json()

        req = self.client.post(
            url=build_url(
                self.endpoint,
                f"/plus/add-item-by-id",
            ),
            content=payload,
            headers=headers,
        )
        self.request = req

        try:
            req.raise_for_status()
        except httpx.HTTPError as exc:
            ze.error_handler(self, req, exc)
        resp = req.json()
        backoff = get_backoff_duration(self.request.headers)
        if backoff:
            self._set_backoff(backoff)
        return resp
