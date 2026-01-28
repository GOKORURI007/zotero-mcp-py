from pyzotero import Zotero


class ZoteroEx(Zotero):
    """
    Local only Zotero API client
    extend from pyzotero.Zotero
    """

    def __init__(
        self,
        library_id: str = '0',
        library_type='user',
        api_key=None,
        preserve_json_order=False,
        locale='en-US',
        local=False,
        client=None,
    ):
        super().__init__()
