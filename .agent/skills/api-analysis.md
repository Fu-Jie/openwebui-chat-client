---
description: 分析 Open WebUI API 并生成客户端代码
---

# API Analysis Skill

此 Skill 用于分析 Open WebUI 的 API 端点信息，并自动生成符合项目规范的同步和异步客户端代码。

## 输入格式

提供 API 端点信息，包括：
1. HTTP 方法 (GET/POST/PUT/DELETE)
2. URL 路径
3. 请求参数 (Query/Body)
4. 响应结构
5. 目标 Manager 名称

## 处理逻辑

1. **分析参数**: 确定必需参数和可选参数，生成类型提示
2. **生成文档**: 根据参数和响应生成 Google 风格的文档字符串
3. **生成同步代码**: 使用 `requests` 实现，包含错误处理
4. **生成异步代码**: 使用 `httpx` 实现，包含错误处理
5. **生成暴露代码**: 生成主客户端的委托调用代码

## 输出示例

```python
# 同步实现 (ChatManager)
def archive_chat(self, chat_id: str) -> bool:
    """
    Archive a chat session.

    Args:
        chat_id: The ID of the chat to archive.

    Returns:
        True if successful, False otherwise.
    """
    try:
        response = self.base_client.session.post(
            f"{self.base_client.base_url}/api/v1/chats/{chat_id}/archive",
            headers=self.base_client.json_headers
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to archive chat {chat_id}: {e}")
        return False

# 异步实现 (AsyncChatManager)
async def archive_chat(self, chat_id: str) -> bool:
    """
    Archive a chat session (Async).

    Args:
        chat_id: The ID of the chat to archive.

    Returns:
        True if successful, False otherwise.
    """
    try:
        response = await self.base_client._make_request(
            "POST", 
            f"/api/v1/chats/{chat_id}/archive"
        )
        return response is not None and response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to archive chat {chat_id}: {e}")
        return False
```

## 使用提示

- 提供尽可能详细的参数描述
- 指明是否需要处理特定的错误状态码
- 说明是否需要特殊的请求头
