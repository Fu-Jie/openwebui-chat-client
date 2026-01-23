# OpenWebUI Chat Client - Agent 开发规则

## 项目概述

**openwebui-chat-client** 是一个全面的、有状态的Python客户端库，用于与 Open WebUI API 进行智能交互。

### 核心目标

- **编程方式创建和管理聊天**: 通过代码创建、查询、管理聊天会话
- **批量与自动化功能**: 提供高效的批量操作和自动化维护脚本
- **全面的API覆盖**: 封装Open WebUI的主要OpenAPI接口

### 技术栈

- **语言**: Python (>=3.8)
- **核心依赖**: `requests`, `httpx`, `python-dotenv`
- **测试框架**: pytest, unittest
- **CI/CD**: GitHub Actions
- **包管理**: PyPI

---

## 架构模式

### 模块化架构

```python
from openwebui_chat_client import OpenWebUIClient

# 客户端使用专门的管理器处理不同功能
client = OpenWebUIClient(base_url, token, default_model)

# 聊天功能 → ChatManager
result = client.chat(question="Hello", chat_title="Test")

# 模型管理 → ModelManager
models = client.list_models()
```

### 同步/异步双客户端

- **同步**: `OpenWebUIClient` (使用 `requests`)
- **异步**: `AsyncOpenWebUIClient` (使用 `httpx`)

每个功能必须同时实现同步和异步版本。

---

## 编码规范

### 类型提示 (必须)

```python
def method_name(
    self,
    param1: str,
    param2: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    pass
```

### 日志记录

- `logger.info()`: 正常操作
- `logger.warning()`: 警告信息
- `logger.error()`: 错误信息
- `logger.debug()`: 调试信息

### 异常处理

- 捕获具体异常类型
- 避免宽泛的 `except Exception`
- 所有异常必须记录日志

### 命名规范

- 内部方法: `_method_name`
- 遵循 PEP 8
- 使用 f-string 格式化

---

## 测试映射

新增功能必须更新 `.github/test-mapping.yml`:

```yaml
file_mappings:
  - pattern: "openwebui_chat_client/**/your_file.py"
    categories: ["your_test_category"]
```

### 测试类别

| 类别 | 描述 |
|------|------|
| `connectivity` | 基础连接 |
| `basic_chat` | 基础聊天 |
| `notes_api` | 笔记 API |
| `prompts_api` | 提示词 API |
| `rag_integration` | RAG 集成 |
| `model_management` | 模型管理 |

---

## CHANGELOG 管理

### 开发期间

```markdown
## [Unreleased]
### Added
- 新增 XXX 功能
```

### 发布准备

1. 将 `[Unreleased]` 转换为版本号
2. **必须删除空的 `[Unreleased]` 部分**
3. 同步更新 `CHANGELOG.zh-CN.md`
4. 同步更新版本号:
   - `pyproject.toml`
   - `openwebui_chat_client/__init__.py`

---

## 关键文件位置

- **主客户端**: `openwebui_chat_client/openwebui_chat_client.py`
- **异步客户端**: `openwebui_chat_client/async_openwebui_client.py`
- **核心模块**: `openwebui_chat_client/core/`
- **功能管理器**: `openwebui_chat_client/modules/`
- **测试**: `tests/`
- **示例**: `examples/`
- **测试映射**: `.github/test-mapping.yml`

---

## 错误处理模式

### 同步客户端

```python
def api_method(self, param: str) -> Optional[Dict[str, Any]]:
    try:
        response = self.base_client.session.post(
            f"{self.base_client.base_url}/api/endpoint",
            headers=self.base_client.json_headers,
            json={"param": param}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}")
        return None
```

### 异步客户端

```python
async def api_method(self, param: str) -> Optional[Dict[str, Any]]:
    try:
        response = await self.base_client._make_request(
            "POST", "/api/endpoint", json_data={"param": param}
        )
        if response and response.status_code == 200:
            return response.json()
        return None
    except httpx.TimeoutException as e:
        logger.error(f"Timeout: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
        return None
```

### 常见错误处理

| 异常类型 | 处理方式 |
|----------|----------|
| 401 Unauthorized | 记录日志，返回 None |
| 404 Not Found | 记录日志，返回 None |
| 连接超时 | 可选重试，记录日志 |
| JSON 解析失败 | 记录原始响应，返回 None |
