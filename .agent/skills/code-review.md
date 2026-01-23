---
description: 代码规范检查和审查
---

# Code Review Skill

此 Skill 用于根据项目规则 (`rules.md`) 审查代码，指出不符合规范的地方并提供修改建议。

## 输入格式

提供 Python 代码片段或文件路径。

## 审查标准

1. **类型提示**: 检查参数和返回值是否有类型提示
2. **文档字符串**: 检查是否包含 Google 风格的文档字符串
3. **错误处理**: 检查是否捕获了具体异常，是否记录了日志
4. **命名规范**: 检查变量和方法命名是否符合 PEP 8
5. **异步规范**: 检查异步代码是否正确使用了 `await` 和 `httpx`

## 输出示例

**问题报告**:
- ❌ **Missing Type Hint**: 参数 `chat_id` 缺少类型提示
- ❌ **Broad Exception**:使用了宽泛的 `except Exception`，建议捕获具体异常
- ⚠️ **Missing Docstring**: 方法缺少文档字符串

**修改建议**:
```python
# 修改前
def get_chat(self, chat_id):
    try:
        return self.client.get(f"/chats/{chat_id}").json()
    except:
        return None

# 修改后
def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
    """Get chat details."""
    try:
        response = self.client.get(f"/chats/{chat_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get chat: {e}")
        return None
```

## 使用提示

- 在提交代码前使用
- 可以配合 `/code-quality` 工作流使用
