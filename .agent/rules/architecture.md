## 🏗️ 架构模式 (立即上手的关键)

### 1. 模块化架构模式

```python
# 主要架构模式 - 理解这个就能立即上手
from openwebui_chat_client import OpenWebUIClient

# 客户端使用专门的管理器处理不同功能
client = OpenWebUIClient(base_url, token, default_model)

# 聊天功能 → ChatManager
result = client.chat(question="Hello", chat_title="Test")

# 模型管理 → ModelManager
models = client.list_models()

# 知识库 → KnowledgeBaseManager
client.create_knowledge_base("my_kb", files=["doc.pdf"])
```

**关键理解**: 所有功能都通过专门的管理器类处理，但API保持向后兼容。

### 2. 状态同步模式

```python
# 客户端维护状态并自动同步到后端
client.chat_id  # 当前活跃聊天ID
client.chat_object_from_server  # 后端聊天对象

# 状态变更自动同步
result = client.chat(question="Hi", chat_title="New Chat")
# ↑ 这会自动创建新聊天并更新 client.chat_id
```

### 3. 选择性集成测试系统

```yaml
# .github/test-mapping.yml - 文件变更到测试的智能映射
file_mappings:
  - pattern: "openwebui_chat_client/**/*chat*.py"
    categories: ["basic_chat", "model_switching"]
  - pattern: "examples/notes_api/**"
    categories: ["notes_api"]
```

**工作流**: 文件变更 → 自动检测 → 只运行相关测试 → 显著提升CI效率

---
