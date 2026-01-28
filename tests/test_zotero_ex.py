from unittest.mock import Mock, patch

from src.zotero_ex import ZoteroEx


class TestZoteroEx:
    def setup_method(self):
        """设置测试环境"""
        self.zotero_ex = ZoteroEx(library_id='12345', library_type='user', api_key='fake_api_key')

    @patch.object(ZoteroEx, 'collections')
    def test_get_collection_key_by_name_found(self, mock_collections):
        """测试当集合存在时能够正确返回key"""
        # 模拟 collections 方法的返回值
        # 注意：key 在顶层，name 在 data 内部，符合实际 API 返回格式
        mock_collections.return_value = [
            {'key': 'AAAAAAA1', 'data': {'name': 'A.Project'}},
            {'key': 'BBBBBBB2', 'data': {'name': '我的出版物'}},
            {'key': 'CCCCCCC3', 'data': {'name': '审稿'}},
            {'key': 'DDDDDDD4', 'data': {'name': '未分类条目'}},
        ]

        # 测试各个集合名称
        assert self.zotero_ex.get_collection_key_by_name('A.Project') == 'AAAAAAA1'
        assert self.zotero_ex.get_collection_key_by_name('我的出版物') == 'BBBBBBB2'
        assert self.zotero_ex.get_collection_key_by_name('审稿') == 'CCCCCCC3'
        assert self.zotero_ex.get_collection_key_by_name('未分类条目') == 'DDDDDDD4'

    @patch.object(ZoteroEx, 'collections')
    def test_get_collection_key_by_name_not_found(self, mock_collections):
        """测试当集合不存在时返回None"""
        # 模拟 collections 方法的返回值
        mock_collections.return_value = [{'key': 'AAAAAAA1', 'data': {'name': 'A.Project'}}]

        # 测试不存在的集合名称
        assert self.zotero_ex.get_collection_key_by_name('不存在的集合') is None
        assert self.zotero_ex.get_collection_key_by_name('') is None
        assert self.zotero_ex.get_collection_key_by_name('Some Other Collection') is None

    @patch.object(ZoteroEx, '_check_backoff')
    @patch.object(ZoteroEx, '_set_backoff')
    @patch('src.zotero_ex.token')
    @patch('src.zotero_ex.build_url')
    def test_add_items_by_identifier_success(
        self, mock_build_url, mock_token, mock_set_backoff, mock_check_backoff
    ):
        """测试add_items_by_identifier方法成功添加项目"""
        # 设置模拟构建的 URL
        expected_url = 'http://fake.url/plus/add-item-by-id'
        mock_build_url.return_value = expected_url
        mock_token.return_value = 'fake_write_token'

        # 创建模拟响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'success': True, 'items': ['item1']}
        mock_response.headers = {}

        # 替换 client 对象
        original_client = self.zotero_ex.client
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        self.zotero_ex.client = mock_client

        # 调用被测试方法
        result = self.zotero_ex.add_items_by_identifier(
            identifier='10.1000/example.doi', collection_key='AAAAAAA1'
        )

        # 验证结果
        assert result == {'success': True, 'items': ['item1']}

        # 验证是否调用了 post 方法
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args

        # 验证 URL 和请求头 - URL 在 kwargs 中，不是在 args[0]
        assert 'plus/add-item-by-id' in kwargs['url']
        assert kwargs['headers']['Zotero-Write-Token'] == 'fake_write_token'
        assert kwargs['headers']['Content-Type'] == 'application/json'

        # 验证 request 属性是否被设置
        assert self.zotero_ex.request == mock_response

        # 恢复原始 client
        self.zotero_ex.client = original_client

    @patch.object(ZoteroEx, '_check_backoff')
    @patch.object(ZoteroEx, '_set_backoff')
    @patch('src.zotero_ex.token')
    @patch('src.zotero_ex.build_url')
    def test_add_items_by_identifier_with_last_modified(
        self, mock_build_url, mock_token, mock_set_backoff, mock_check_backoff
    ):
        """测试add_items_by_identifier方法带有last_modified参数"""
        # 设置模拟构建的 URL
        expected_url = 'http://fake.url/plus/add-item-by-id'
        mock_build_url.return_value = expected_url
        mock_token.return_value = 'fake_write_token'

        # 创建模拟响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'success': True, 'items': ['item1']}
        mock_response.headers = {}

        # 替换 client 对象
        original_client = self.zotero_ex.client
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        self.zotero_ex.client = mock_client

        # 调用被测试方法，带 last_modified 参数
        result = self.zotero_ex.add_items_by_identifier(
            identifier='10.1000/example.doi', collection_key='AAAAAAA1', last_modified=12345
        )

        # 验证结果
        assert result == {'success': True, 'items': ['item1']}

        # 验证是否调用了 post 方法
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args

        # 验证 URL 和请求头，特别是 If-Unmodified-Since-Version
        assert 'plus/add-item-by-id' in kwargs['url']
        assert kwargs['headers']['Zotero-Write-Token'] == 'fake_write_token'
        assert kwargs['headers']['Content-Type'] == 'application/json'
        assert kwargs['headers']['If-Unmodified-Since-Version'] == '12345'

        # 验证 request 属性是否被设置
        assert self.zotero_ex.request == mock_response

        # 恢复原始 client
        self.zotero_ex.client = original_client

    @patch.object(ZoteroEx, 'collections')
    def test_get_collection_key_by_name_empty_collections(self, mock_collections):
        """测试当没有集合时返回None"""
        # 模拟 collections 方法返回空列表
        mock_collections.return_value = []

        # 测试任何集合名称都应该返回 None
        assert self.zotero_ex.get_collection_key_by_name('A.Project') is None
        assert self.zotero_ex.get_collection_key_by_name('Some Collection') is None

    @patch.object(ZoteroEx, '_check_backoff')
    @patch.object(ZoteroEx, '_set_backoff')
    @patch('src.zotero_ex.build_url')
    def test_get_selected_collection_success(
        self, mock_build_url, mock_set_backoff, mock_check_backoff
    ):
        """测试get_selected_collection方法成功获取选中集合信息"""
        # 设置模拟构建的 URL
        expected_url = 'http://fake.url/plus/selected-collection'
        mock_build_url.return_value = expected_url

        # 创建模拟响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'key': 'SELECTED1',
            'data': {'name': '当前选中集合', 'type': 'collection'}
        }
        mock_response.headers = {}

        # 替换 client 对象
        original_client = self.zotero_ex.client
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        self.zotero_ex.client = mock_client

        # 调用被测试方法
        result = self.zotero_ex.get_selected_collection()

        # 验证结果
        assert result == {
            'key': 'SELECTED1',
            'data': {'name': '当前选中集合', 'type': 'collection'}
        }

        # 验证是否调用了 get 方法
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args

        # 验证 URL 和请求头
        assert 'plus/selected-collection' in kwargs['url']
        assert kwargs['headers']['Content-Type'] == 'application/json'

        # 验证 request 属性是否被设置
        assert self.zotero_ex.request == mock_response

        # 恢复原始 client
        self.zotero_ex.client = original_client
