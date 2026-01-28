from typing import Literal

import httpx
from pyzotero import Zotero
from pyzotero import errors as ze
from pyzotero._utils import build_url, get_backoff_duration, token

from src import config
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
            library_id, library_type, api_key, preserve_json_order, locale, local, client
        )

        self.endpoint = config.ENDPOINT

    def add_items_by_identifier(
        self, identifier: str, collection_key: str, last_modified=None
    ) -> dict[str, str | list[str]]:
        headers = {'Zotero-Write-Token': token(), 'Content-Type': 'application/json'}
        if last_modified is not None:
            headers['If-Unmodified-Since-Version'] = str(last_modified)
        self._check_backoff()

        payload = AddByIDPayload(
            identifier=identifier, collectionKey=collection_key
        ).model_dump_json()

        req = self.client.post(
            url=build_url(
                self.endpoint,
                '/plus/add-item-by-id',
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

    def get_collection_key_by_name(self, collection_name: str) -> str | None:
        """
        根据集合名称获取集合的 key

        Args:
            collection_name (str): 集合名称

        Returns:
            str or None: 如果找到则返回集合的 key，否则返回 None
        """

        # 获取所有集合
        collections = self.collections()

        # 遍历查找匹配的集合名称
        for collection in collections:
            if collection.get('data', {}).get('name') == collection_name:
                return collection.get('key')

        # 如果没有找到匹配的集合，返回 None
        return None

    def get_selected_collection(self) -> dict[str, str | list[str]]:
        """
        获取当前选择的 collection 的信息

        Returns:
            dict: 当前选择的 collection 的信息
        """
        headers = {'Content-Type': 'application/json'}
        self._check_backoff()

        req = self.client.get(
            url=build_url(
                self.endpoint,
                '/plus/selected-collection',
            ),
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
