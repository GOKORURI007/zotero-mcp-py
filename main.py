import os

import httpx
from pyzotero import Zotero

from src.zotero_ex import ZoteroEx


def main():
    # 设置 NO_PROXY 环境变量, 让 httpx 跳过 localhost 的代理
    old_no_proxy = os.environ.get('NO_PROXY', '')
    old_no_proxy_lower = os.environ.get('no_proxy', '')

    # 添加 localhost 到 NO_PROXY 列表
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'

    try:
        print('正在连接本地Zotero...')
        zot = ZoteroEx()
        zot.all_collections()
        print('正在获取数据...')
        try:
            zot.add_items_by_identifier(
                'https://doi.org/10.1109/CVPR52733.2024.01770',
                'WVNC398Z'
            )
        except Exception as e:
            print(e)
            raise
    finally:
        # 恢复 NO_PROXY 设置
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
