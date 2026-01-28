#!/usr/bin/env nix-shell
# !nix-shell -i python3 -p "python3.withPackages(ps: [ps.mcp ps.httpx])"

from fastmcp import FastMCP

from src import ZoteroEx

# 初始化 FastMCP
# 如果以后要给 Chatbox 用 SSE，启动时加参数即可，代码基本不用动
mcp = FastMCP(name='zotero-mcp-py', instructions='Zotero control')
zot = ZoteroEx()


@mcp.tool()
async def add_item_by_identifier_to_collection(
    identifier: str, collection_key: str = None, collection_name: str = None
) -> dict[str, str | list[str]] | None:
    """
    Use Zotero's Magic Wand to add a paper by DOI, ISBN, arXiv ID, or URL.

    Args:
        identifier: The DOI, URL, or identifier of the paper.
        collection_key: Optional 8-character Zotero collection key (e.g., 'XDXSZPNA').
        collection_name: Zotero collection name.
    """
    if not collection_key and not collection_name:
        collection_key = zot.collections_top
    if collection_key:
        return zot.add_items_by_identifier(identifier, collection_key)
    elif collection_name:
        collection_key = zot.get_collection_key_by_name(collection_name)
        if collection_key:
            return zot.add_items_by_identifier(identifier, collection_key)
    return None


if __name__ == '__main__':
    # 默认使用 stdio 模式，适合 Cursor/Claude Desktop
    mcp.run()
