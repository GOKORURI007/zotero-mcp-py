import os

from fastmcp import FastMCP
from loguru import logger

from src import ZoteroEx

# 初始化 FastMCP
# 如果以后要给 Chatbox 用 SSE，启动时加参数即可，代码基本不用动
mcp = FastMCP(name='zotero-mcp-py', instructions='Zotero control')
mcp.zot = ZoteroEx()


@mcp.tool()
async def add_item_by_identifier_to_collection(
    identifier: str, collection_key: str | None = None, collection_name: str | None = None
) -> str:
    """
    Add a paper into a collection by DOI, ISBN, arXiv ID, or URL.
    If no collection is specified, it will use the currently selected collection in Zotero.

    Args:
        identifier: The DOI, URL, or identifier of the paper.
        collection_key: Optional 8-character Zotero collection key (e.g., 'XDXSZPNA').
        collection_name: Optional name of the target collection.
    """
    try:
        # 1. 确定目标 Collection Key
        logger.debug('MCP Call Received!')
        logger.debug(f' > Identifier: {identifier}')
        logger.debug(f' > Collection: {collection_name or collection_key}')

        target_key = collection_key
        if not target_key and collection_name:
            target_key = mcp.zot.get_collection_key_by_name(collection_name)
            if not target_key:
                msg = f"Error: Could not find a collection named '{collection_name}'."
                logger.debug('msg')
                return msg

        # 如果还是没有 key，尝试获取当前选中的分类
        if not target_key:
            current_col = mcp.zot.get_selected_collection()
            if current_col and 'key' in current_col:
                target_key = current_col['key']
            else:
                msg = 'Error: No collection specified and no collection is currently selected in Zotero.'
                logger.debug(msg)
                return msg

        # 2. 调用 Zotero 本地接口 (假设 zot.add_items_by_identifier 返回响应对象或元组)
        # 这里的 resp 应该是你之前定义的 [status_code, content_type, body]
        resp = mcp.zot.add_items_by_identifier(identifier, target_key)

        # 3. 根据状态码进行分支处理
        if resp.status_code == 200:
            import json

            data = json.loads(resp.text)
            titles = ', '.join([f'{t}' for t in data.get('titles', [])])
            msg = f'✅ Success: Added {data.get("addedCount")} item(s) to collection [{target_key}]. Titles: {titles}'
            logger.debug(msg)
            return msg

        elif resp.status_code == 400:
            if 'No identifier' in resp.text:
                return '❌ Failure: The identifier provided was empty.'
            msg = f"❌ Failure: Zotero could not parse the identifier '{identifier}'. Please check if the DOI/URL is valid."
            logger.debug(msg)
            return msg

        elif resp.status_code == 404:
            msg = "❌ Failure: No bibliographic data found. This ID might not exist in Zotero's translation servers."
            logger.debug(msg)
            return msg

        elif resp.status_code == 500:
            msg = f'🚫 System Error: Zotero internal error - {resp.text}'
            logger.debug(msg)
            return msg

        else:
            msg = f'⚠️ Unexpected response (Code {resp.status_code}): {resp.text}'
            logger.debug(msg)
            return msg

    except Exception as e:
        msg = f'🚫 Bridge Error: Failed to communicate with Zotero. Ensure Zotero is running and the MCP plugin is active. Details: {str(e)}'
        logger.debug(msg)
        return msg


if __name__ == '__main__':
    # 默认使用 stdio 模式，适合 Cursor/Claude Desktop
    old_no_proxy = os.environ.get('NO_PROXY', '')
    old_no_proxy_lower = os.environ.get('no_proxy', '')
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'
    try:
        mcp.run(transport='sse', host='127.0.0.1', port=9999)
    finally:
        if old_no_proxy:
            os.environ['NO_PROXY'] = old_no_proxy
        else:
            os.environ.pop('NO_PROXY', None)

        if old_no_proxy_lower:
            os.environ['no_proxy'] = old_no_proxy_lower
        else:
            os.environ.pop('no_proxy', None)
