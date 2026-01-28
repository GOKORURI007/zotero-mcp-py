import os

import pytest


@pytest.fixture(autouse=True)
def bypass_proxy():
    """测试开始时绕过所有proxy，结束后恢复"""
    # 保存原始环境变量
    original_http_proxy = os.environ.get('HTTP_PROXY')
    original_https_proxy = os.environ.get('HTTPS_PROXY')
    original_no_proxy = os.environ.get('NO_PROXY')

    # 绕过所有代理
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    os.environ['NO_PROXY'] = '*'

    yield  # 执行测试

    # 恢复原始环境变量
    if original_http_proxy is not None:
        os.environ['HTTP_PROXY'] = original_http_proxy
    else:
        os.environ.pop('HTTP_PROXY', None)

    if original_https_proxy is not None:
        os.environ['HTTPS_PROXY'] = original_https_proxy
    else:
        os.environ.pop('HTTPS_PROXY', None)

    if original_no_proxy is not None:
        os.environ['NO_PROXY'] = original_no_proxy
    else:
        os.environ.pop('NO_PROXY', None)
