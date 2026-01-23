---
description: 新增 API 端点的完整流程
---

# 新增 API 端点流程

## 1. 需求分析

### 确认 API 端点信息
1. HTTP 方法 (GET/POST/PUT/DELETE)
2. 端点路径 (如 `/api/v1/chats/{id}`)
3. 请求参数和响应格式
4. 认证要求

### 查看 Open WebUI API 文档
```
http://localhost:3000/docs
```

## 2. 确定目标模块

### Manager 模块对应关系
| 功能领域 | 同步 Manager | 异步 Manager |
|----------|--------------|--------------|
| 聊天 | `ChatManager` | `AsyncChatManager` |
| 模型 | `ModelManager` | `AsyncModelManager` |
| 文件 | `FileManager` | `AsyncFileManager` |
| 知识库 | `KnowledgeBaseManager` | `AsyncKnowledgeBaseManager` |
| 笔记 | `NotesManager` | `AsyncNotesManager` |
| 提示词 | `PromptsManager` | `AsyncPromptsManager` |
| 用户 | `UserManager` | `AsyncUserManager` |

## 3. 实现同步版本

### 在 Manager 中添加方法
```python
# openwebui_chat_client/modules/<manager>.py

def new_api_method(
    self,
    param1: str,
    param2: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    方法描述。

    Args:
        param1: 参数描述
        param2: 可选参数描述

    Returns:
        返回值描述，或 None 如果失败
    """
    logger.info(f"Calling new_api_method with param1={param1}")
    
    try:
        response = self.base_client.session.post(
            f"{self.base_client.base_url}/api/v1/endpoint",
            headers=self.base_client.json_headers,
            json={"param1": param1, "param2": param2}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to call new_api_method: {e}")
        return None
```

### 在主客户端中暴露
```python
# openwebui_chat_client/openwebui_chat_client.py

def new_api_method(self, param1: str, ...) -> Optional[Dict[str, Any]]:
    """文档字符串"""
    return self._manager.new_api_method(param1, ...)
```

## 4. 实现异步版本

### 在异步 Manager 中添加方法
```python
# openwebui_chat_client/modules/async_<manager>.py

async def new_api_method(
    self,
    param1: str,
    param2: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """异步版本文档字符串"""
    logger.info(f"Calling new_api_method with param1={param1}")
    
    try:
        response = await self.base_client._make_request(
            "POST", "/api/v1/endpoint", json_data={"param1": param1}
        )
        if response and response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Failed to call new_api_method: {e}")
        return None
```

### 在异步客户端中暴露
```python
# openwebui_chat_client/async_openwebui_client.py

async def new_api_method(self, param1: str, ...) -> Optional[Dict[str, Any]]:
    """文档字符串"""
    return await self._manager.new_api_method(param1, ...)
```

## 5. 格式化和检查

// turbo
```bash
make format
make check
```

## 6. 添加测试

### 单元测试
```python
# tests/test_new_api.py

def test_new_api_method_success(self):
    """测试成功场景"""
    pass

def test_new_api_method_failure(self):
    """测试失败场景"""
    pass
```

### 运行测试
// turbo
```bash
pytest tests/test_new_api.py -v
```

## 7. 更新测试映射

编辑 `.github/test-mapping.yml`:
```yaml
file_mappings:
  - pattern: "openwebui_chat_client/**/*new_feature*.py"
    categories: ["new_feature"]
```

## 8. 更新 CHANGELOG

```markdown
### Added
- 新增 `new_api_method` 方法，支持 XXX 功能
```
