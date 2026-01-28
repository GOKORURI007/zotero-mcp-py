import os

import httpx
from pyzotero import Zotero


def main():
    # 设置NO_PROXY环境变量,让httpx跳过localhost的代理
    old_no_proxy = os.environ.get('NO_PROXY', '')
    old_no_proxy_lower = os.environ.get('no_proxy', '')

    # 添加localhost到NO_PROXY列表
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'

    try:
        # 创建自定义客户端
        custom_client = httpx.Client(
            headers={
                'User-Agent': 'Pyzotero/1.8.0',
            },
            follow_redirects=True,
            timeout=30.0,  # 设置超时时间
        )
        print('正在连接本地Zotero...')
        zot = Zotero(
            library_id='0',
            library_type='user',
            local=True,
            client=custom_client,  # 使用自定义客户端
        )

        print('正在获取数据...')
        try:
            items = zot.items()
            print(f'获取到 {len(items)} 条数据')
            if items:
                print(f'第一条数据: {items[0].get("data", {}).get("title", "No title")}')
            return items
        except Exception as e:
            print(f'错误: {type(e).__name__}: {e}')
            raise
    finally:
        # 恢复NO_PROXY设置
        if old_no_proxy:
            os.environ['NO_PROXY'] = old_no_proxy
        else:
            os.environ.pop('NO_PROXY', None)

        if old_no_proxy_lower:
            os.environ['no_proxy'] = old_no_proxy_lower
        else:
            os.environ.pop('no_proxy', None)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
