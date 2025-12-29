# API 参考

本页面提供 `openwebui-chat-client` 的完整 API 参考，从源代码文档字符串自动生成。

---

## OpenWebUIClient

用于同步操作的主客户端类。

::: openwebui_chat_client.OpenWebUIClient
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - chat
        - stream_chat
        - parallel_chat
        - continuous_chat
        - continuous_parallel_chat
        - continuous_stream_chat
        - deep_research
        - process_task
        - stream_process_task
        - rename_chat
        - set_chat_tags
        - update_chat_metadata
        - switch_chat_model
        - list_chats
        - get_chats_by_folder
        - archive_chat
        - archive_chats_by_age
        - delete_all_chats
        - create_folder
        - get_folder_id_by_name
        - move_chat_to_folder
        - list_models
        - list_base_models
        - list_custom_models
        - list_groups
        - get_model
        - create_model
        - update_model
        - delete_model
        - batch_update_model_permissions
        - get_knowledge_base_by_name
        - create_knowledge_base
        - add_file_to_knowledge_base
        - delete_knowledge_base
        - delete_all_knowledge_bases
        - delete_knowledge_bases_by_keyword
        - create_knowledge_bases_with_files
        - get_notes
        - get_notes_list
        - create_note
        - get_note_by_id
        - update_note_by_id
        - delete_note_by_id
        - get_prompts
        - get_prompts_list
        - create_prompt
        - get_prompt_by_command
        - update_prompt_by_command
        - replace_prompt_by_command
        - delete_prompt_by_command
        - search_prompts
        - extract_variables
        - substitute_variables
        - get_system_variables
        - batch_create_prompts
        - batch_delete_prompts
        - get_users
        - get_user_by_id
        - update_user_role
        - delete_user

---

## AsyncOpenWebUIClient

用于异步操作的异步客户端类。

::: openwebui_chat_client.AsyncOpenWebUIClient
    options:
      show_root_heading: true
      show_source: false

---

## 返回值示例

### 聊天操作

```python
{
    "response": "生成的响应文本",
    "chat_id": "chat-uuid-string",
    "message_id": "message-uuid-string",
    "sources": [...]  # 用于 RAG 操作
}
```

### 并行聊天

```python
{
    "responses": {
        "model-1": "模型 1 的响应",
        "model-2": "模型 2 的响应"
    },
    "chat_id": "chat-uuid-string",
    "message_ids": {
        "model-1": "message-uuid-1",
        "model-2": "message-uuid-2"
    }
}
```

### 知识库 / 笔记

```python
{
    "id": "resource-uuid",
    "name": "资源名称",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    ...
}
```

### 任务处理

```python
{
    "solution": "最终解决方案文本",
    "conversation_history": [...],  # 或摘要字符串
    "todo_list": [
        {"task": "研究主题", "status": "completed"},
        {"task": "撰写摘要", "status": "completed"}
    ]
}
```

---

## 快速参考表

### 聊天操作

| 方法 | 描述 |
|------|------|
| `chat()` | 带可选功能的单模型对话 |
| `stream_chat()` | 带实时更新的流式对话 |
| `parallel_chat()` | 多模型并行对话 |
| `continuous_chat()` | 带后续问题的连续对话 |
| `process_task()` | 自主多步骤任务处理 |
| `deep_research()` | 多步骤研究代理 |

### 聊天管理

| 方法 | 描述 |
|------|------|
| `rename_chat()` | 重命名现有聊天 |
| `set_chat_tags()` | 为聊天应用标签 |
| `update_chat_metadata()` | 重新生成标签和/或标题 |
| `switch_chat_model()` | 切换现有聊天的模型 |
| `list_chats()` | 获取用户的聊天列表 |
| `archive_chat()` | 归档特定聊天 |
| `archive_chats_by_age()` | 批量归档旧聊天 |
| `create_folder()` | 创建聊天文件夹 |

### 模型管理

| 方法 | 描述 |
|------|------|
| `list_models()` | 列出可用模型 |
| `list_base_models()` | 列出基础模型 |
| `list_custom_models()` | 列出自定义模型 |
| `get_model()` | 获取模型详情 |
| `create_model()` | 创建自定义模型 |
| `update_model()` | 更新模型 |
| `delete_model()` | 删除模型 |
| `batch_update_model_permissions()` | 批量更新权限 |

### 知识库操作

| 方法 | 描述 |
|------|------|
| `create_knowledge_base()` | 创建知识库 |
| `add_file_to_knowledge_base()` | 向知识库添加文件 |
| `get_knowledge_base_by_name()` | 按名称获取知识库 |
| `delete_knowledge_base()` | 删除知识库 |
| `delete_all_knowledge_bases()` | 删除所有知识库 |
| `create_knowledge_bases_with_files()` | 批量创建知识库 |

### 笔记 API

| 方法 | 描述 |
|------|------|
| `get_notes()` | 获取所有笔记 |
| `create_note()` | 创建笔记 |
| `get_note_by_id()` | 按 ID 获取笔记 |
| `update_note_by_id()` | 更新笔记 |
| `delete_note_by_id()` | 删除笔记 |

### 提示词 API

| 方法 | 描述 |
|------|------|
| `get_prompts()` | 获取所有提示词 |
| `create_prompt()` | 创建提示词 |
| `get_prompt_by_command()` | 按命令获取提示词 |
| `update_prompt_by_command()` | 更新提示词 |
| `delete_prompt_by_command()` | 删除提示词 |
| `extract_variables()` | 提取提示词变量 |
| `substitute_variables()` | 替换变量 |

### 用户管理

| 方法 | 描述 |
|------|------|
| `get_users()` | 列出用户 |
| `get_user_by_id()` | 获取用户详情 |
| `update_user_role()` | 更新用户角色 |
| `delete_user()` | 删除用户 |
