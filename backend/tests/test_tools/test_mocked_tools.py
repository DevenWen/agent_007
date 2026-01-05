"""简化的 Mock Tools 测试"""

import pytest
from unittest.mock import AsyncMock, patch, mock_open


@pytest.mark.unit
class TestFileTools:
    """测试 File Tools（使用 mock）"""

    @patch("builtins.open", new_callable=mock_open, read_data="test content")
    async def test_read_file(self, mock_file):
        """测试读取文件"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        read_file = tools["read_file"].original_func

        result = await read_file({"path": "/test/file.txt"})
        assert "content" in result or "Content" in result

    @patch("builtins.open", new_callable=mock_open)
    async def test_write_file(self, mock_file):
        """测试写入文件"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        write_file = tools["write_file"].original_func

        result = await write_file({"path": "/test/file.txt", "content": "test content"})
        assert "success" in result.lower() or "written" in result.lower()


@pytest.mark.unit
class TestHttpTools:
    """测试 HTTP Tools（使用 mock）"""

    @patch("httpx.AsyncClient")
    async def test_http_request(self, mock_client):
        """测试 HTTP 请求"""
        from app.tools.registry import get_all_registered_tools

        # Mock HTTP 响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "test response"
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        tools = get_all_registered_tools()
        http_request = tools["http_request"].original_func

        result = await http_request({"method": "GET", "url": "https://example.com"})
        assert "200" in result or "success" in result.lower()
