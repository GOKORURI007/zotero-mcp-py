import os

from src.zotero_mcp import mcp


def main():
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


if __name__ == '__main__':
    main()
