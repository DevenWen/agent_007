"""HTTP 请求工具"""

import re
import httpx
from typing import Any
from app.tools.registry import register_tool


@register_tool(
    name="http_request",
    description="发送 HTTP 请求",
    input_schema={"url": str, "method": str, "headers": dict, "body": str},
)
async def http_request(params: dict[str, Any]) -> str:
    """发送 HTTP 请求

    Args:
        params: {
            "url": "请求 URL",
            "method": "请求方法 (GET/POST/PUT/DELETE)",
            "headers": {"key": "value"},
            "body": "请求体"
        }

    Returns:
        响应内容或错误信息
    """
    url = params.get("url", "")
    method = params.get("method", "GET").upper()
    headers = params.get("headers", {})
    body = params.get("body", "")

    if not url:
        return "Error: 'url' parameter is required"

    if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]:
        return f"Error: Unsupported method: {method}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body if body else None,
            )

        # 构建响应
        result_parts = [
            f"Status: {response.status_code}",
            f"Headers: {dict(response.headers)}",
        ]

        # 响应体
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                result_parts.append(f"Body (JSON):\n{response.json()}")
            except Exception:
                result_parts.append(f"Body:\n{response.text[:10000]}")
        else:
            body_text = response.text
            if len(body_text) > 10000:
                body_text = body_text[:10000] + "\n... (truncated)"
            result_parts.append(f"Body:\n{body_text}")

        return "\n\n".join(result_parts)

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except httpx.RequestError as e:
        return f"Error: Request failed: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@register_tool(
    name="fetch_webpage", description="抓取网页内容", input_schema={"url": str}
)
async def fetch_webpage(params: dict[str, Any]) -> str:
    """抓取网页内容

    Args:
        params: {"url": "网页 URL"}

    Returns:
        网页文本内容或错误信息
    """
    url = params.get("url", "")
    if not url:
        return "Error: 'url' parameter is required"

    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AgentPlatform/1.0)"},
        ) as client:
            response = await client.get(url)

        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"

        content = response.text

        # 简单的 HTML 到文本转换（移除标签）
        # 移除 script 和 style 标签及其内容
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        content = re.sub(
            r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        # 移除 HTML 标签
        content = re.sub(r"<[^>]+>", " ", content)
        # 清理空白
        content = re.sub(r"\s+", " ", content).strip()

        # 限制长度
        if len(content) > 50000:
            content = content[:50000] + "\n... (content truncated)"

        return content

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except httpx.RequestError as e:
        return f"Error: Request failed: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
