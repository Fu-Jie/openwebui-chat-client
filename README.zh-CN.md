# OpenWebUI Python 客户端

[English](./README.md) | [简体中文](./README.zh-CN.md)

[![PyPI 版本](https://img.shields.io/pypi/v/openwebui-chat-client/0.1.13?style=flat-square&color=brightgreen)](https://pypi.org/project/openwebui-chat-client/)
[![更新日志](https://img.shields.io/badge/更新日志-v0.1.12-blue.svg)](./CHANGELOG.zh-CN.md)
[![许可证: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![支持的 Python 版本](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

**openwebui-chat-client** 是面向 [Open WebUI](https://github.com/open-webui/open-webui) API 的状态化 Python 客户端库，支持单/多模型对话、工具调用、文件上传、RAG、知识库管理和高级聊天组织。

> [!IMPORTANT]
> 本项目正处于积极开发阶段，API 可能会在未来版本中发生变化。请查阅最新文档和 [CHANGELOG.zh-CN.md](./CHANGELOG.zh-CN.md) 以获取最新信息。

---

## 🚀 安装

```bash
pip install openwebui-chat-client
```

---

## ⚡ 快速开始

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

# chat 方法返回一个包含回复、chat_id 和 message_id 的字典
result = client.chat(
    question="你好，你怎么样？",
    chat_title="我的第一次聊天"
)
if result:
    print(f"回复: {result['response']}")
    print(f"Chat ID: {result['chat_id']}")
```

---

## ✨ 主要功能

- **自动元数据生成**: 为您的对话自动生成标签和标题。
- **手动元数据更新**: 按需为现有对话重新生成标签和标题。
- **实时流式聊天更新**: 在流式聊天期间体验打字机效果的实时内容更新。
- **聊天追问生成选项**: 支持在聊天方法中生成追问问题或选项。
- 多模态对话：文本、图片、文件上传
- 单模型 & 并行模型对话（A/B 测试）
- 工具集成：在对话中调用服务器端工具
- RAG 检索增强：文件/知识库辅助回复
- 知识库管理：创建、更新、查询
- 模型管理：列出、创建、更新、删除自定义模型条目，并增强了 `get_model` 的自动创建/重试功能。
- 聊天组织：重命名、文件夹、标签、搜索
- **并发处理**: 并行模型查询，实现快速多模型响应。

---

## 🧑‍💻 基本示例

### 单模型对话

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

result = client.chat(
    question="介绍一下 OpenAI GPT-4.1 的主要功能？",
    chat_title="GPT-4.1 功能演示"
)
if result:
    print(result['response'])
```

### 并行模型对话

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="你的令牌",
    default_model_id="gpt-4.1"
)

result = client.parallel_chat(
    question="比较 GPT-4.1 和 Gemini 2.5 Flash 在文档摘要方面的优势。",
    chat_title="模型对比",
    model_ids=["gpt-4.1", "gemini-2.5-flash"],
    folder_name="技术对比" # 你可以选择将聊天整理到文件夹中
)
if result and result.get("responses"):
    for model, resp in result["responses"].items():
        print(f"{model} 回复:\n{resp}\n")
    print(f"聊天已保存，ID: {result.get('chat_id')}")
```

### 🖥️ 示例：页面渲染 (Web UI 集成)

运行上述 Python 代码后，你可以在 Open WebUI 网页界面中查看对话和模型比较结果：

- **单模型** (`gpt-4.1`):  
  聊天记录将在对话时间线中显示你的输入问题和 GPT-4.1 模型的回应。  
  ![单模型对话示例](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/single-model-chat.png)

- **并行模型** (`gpt-4.1` & `gemini-2.5-flash`):  
  聊天将并排（或分组）显示两个模型对同一输入的响应，通常会按模型进行标记或颜色编码。  
  ![并行模型比较示例](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/parallel-model-chat.png)

> **提示:**  
> Web UI 会使用模型名称来直观地区分响应。你可以展开、折叠或复制每个答案，还可以在界面中直接对聊天进行标记、整理和搜索。

---

## 🧠 高级聊天示例

### 1. 使用工具 (函数)

如果你的 Open WebUI 实例中配置了工具（例如天气工具或网页搜索工具），你可以在请求中指定使用哪些工具。

```python
# 假设你的服务器上配置了一个 ID 为 'search-the-web-tool' 的工具。
# 这个工具需要在 Open WebUI 的“工具”部分创建。

result = client.chat(
    question="欧盟人工智能监管的最新进展是什么？",
    chat_title="AI 监管新闻",
    model_id="gpt-4.1",
    tool_ids=["search-the-web-tool"] # 传入要使用的工具 ID
)

if result:
    print(result['response'])
```

### 2. 多模态聊天 (带图片)

将图片与文本提示一起发送给支持视觉的模型。

```python
# 确保 'chart.png' 存在于你的脚本所在的目录中。
# 模型 'gpt-4.1' 支持视觉功能。

result = client.chat(
    question="请分析附带的销售图表，并提供趋势摘要。",
    chat_title="销售图表分析",
    model_id="gpt-4.1",
    image_paths=["./chart.png"] # 图片的本地文件路径列表
)

if result:
    print(result['response'])
```

### 3. 在同一聊天中切换模型

你可以用一个模型开始对话，然后切换到另一个模型进行后续提问，所有这些都在同一个聊天历史中。客户端无缝处理状态。

```python
# 用一个强大的通用模型开始聊天
result_1 = client.chat(
    question="用简单的语言解释相对论。",
    chat_title="科学与速度",
    model_id="gpt-4.1"
)
if result_1:
    print(f"GPT-4.1 回答: {result_1['response']}")

# 现在，在同一个聊天中提出一个不同的问题，但切换到一个快速高效的模型
result_2 = client.chat(
    question="现在，陆地上跑得最快的 3 种动物是什么？",
    chat_title="科学与速度",   # 使用相同的标题继续聊天
    model_id="gemini-2.5-flash"  # 切换到不同的模型
)
if result_2:
    print(f"\nGemini 2.5 Flash 回答: {result_2['response']}")

# 两个结果的 chat_id 将相同。
if result_1 and result_2:
    print(f"\n两次交互的 Chat ID: {result_1['chat_id']}")
```

### 4. 批量模型权限管理

您可以一次性管理多个模型的权限，支持公共、私有和基于群组的访问控制。

```python
# 将多个模型设置为公共访问
result = client.batch_update_model_permissions(
    model_identifiers=["gpt-4.1", "gemini-2.5-flash"],
    permission_type="public"
)

# 将包含"gpt"的所有模型设置为特定用户的私有访问
result = client.batch_update_model_permissions(
    model_keyword="gpt",
    permission_type="private",
    user_ids=["user-id-1", "user-id-2"]
)

# 使用群组名称将模型设置为基于群组的权限
result = client.batch_update_model_permissions(
    model_keyword="claude",
    permission_type="group",
    group_identifiers=["admin", "normal"]  # 群组名称将被解析为ID
)

print(f"✅ 成功更新: {len(result['success'])} 个模型")
print(f"❌ 更新失败: {len(result['failed'])} 个模型")

# 列出可用于权限管理的群组
groups = client.list_groups()
if groups:
    for group in groups:
        print(f"群组: {group['name']} (ID: {group['id']})")
```

### 5. 归档聊天会话

您可以单独归档聊天会话，或根据其时间和文件夹组织进行批量归档。

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient("http://localhost:3000", "your_token_here", "gpt-4.1")

# 归档特定聊天
success = client.archive_chat("chat-id-here")
if success:
    print("✅ 聊天归档成功")

# 批量归档超过30天且不在文件夹中的聊天
results = client.archive_chats_by_age(days_since_update=30)
print(f"已归档 {results['total_archived']} 个聊天")

# 批量归档特定文件夹中超过7天的聊天
results = client.archive_chats_by_age(
    days_since_update=7, 
    folder_name="旧项目"
)
print(f"从文件夹归档了 {results['total_archived']} 个聊天")

# 获取详细结果
for chat in results['archived_chats']:
    print(f"已归档: {chat['title']}")

for chat in results['failed_chats']:
    print(f"失败: {chat['title']} - {chat['error']}")
```

**归档逻辑:**
- **无文件夹过滤**: 仅归档不在任何文件夹中的聊天
- **有文件夹过滤**: 仅归档在指定文件夹中的聊天
- **时间过滤**: 仅归档在指定天数内未更新的聊天
- **并行处理**: 使用并发处理提高批量操作效率

---

## 🔑 如何获取你的 API 密钥

1. 登录你的 Open WebUI 账户。
2. 点击左下角的个人资料图片/名称，然后进入 **设置**。
3. 在设置菜单中，导航到 **账户** 部分。
4. 找到 **API 密钥** 区域并 **创建新密钥**。
5. 复制生成的密钥，并将其设置为你的 `OUI_AUTH_TOKEN` 环境变量，或直接在客户端代码中使用。

---

## 📚 API 参考

### 💬 聊天操作

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `chat()` | 启动/继续单模型对话，支持追问生成选项 | `question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |
| `stream_chat()` | 启动/继续单模型流式对话，支持实时更新 | `question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |
| `parallel_chat()` | 启动/继续多模型并行对话 | `question, chat_title, model_ids, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling` |

### 🛠️ 聊天管理

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `rename_chat()` | 重命名现有聊天 | `chat_id, new_title` |
| `set_chat_tags()` | 为聊天应用标签 | `chat_id, tags` |
| `update_chat_metadata()` | 为现有聊天重新生成和更新标签和/或标题 | `chat_id, regenerate_tags, regenerate_title` |
| `switch_chat_model()` | 切换现有聊天的模型 | `chat_id, new_model_id` |
| `create_folder()` | 创建聊天文件夹进行组织 | `folder_name` |
| `list_chats()` | 获取用户聊天列表，支持分页 | `page` |
| `get_chats_by_folder()` | 获取特定文件夹中的聊天 | `folder_id` |
| `archive_chat()` | 归档特定聊天 | `chat_id` |
| `archive_chats_by_age()` | 基于时间和文件夹条件批量归档聊天 | `days_since_update, folder_name` |

### 🤖 模型管理

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `list_models()` | 列出所有可用模型条目，提高了可靠性 | None |
| `list_base_models()` | 列出所有可用基础模型，提高了可靠性 | None |
| `list_groups()` | 列出所有可用的权限管理用户组 | None |
| `get_model()` | 获取特定模型的详细信息，支持自动重试创建 | `model_id` |
| `create_model()` | 创建详细的自定义模型变体 | `model_config` |
| `update_model()` | 使用细粒度更改更新现有模型条目 | `model_id, access_control, **kwargs` |
| `delete_model()` | 从服务器删除模型条目 | `model_id` |
| `batch_update_model_permissions()` | 批量更新多个模型的访问控制权限 | `model_identifiers, model_keyword, permission_type, group_identifiers, user_ids, max_workers` |

### 📚 知识库操作

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `create_knowledge_base()` | 创建新的知识库 | `name, description` |
| `add_file_to_knowledge_base()` | 向现有知识库添加文件 | `kb_id, file_path` |
| `get_knowledge_base_by_name()` | 根据名称检索知识库 | `name` |
| `delete_knowledge_base()` | 根据ID删除特定知识库 | `kb_id` |
| `delete_all_knowledge_bases()` | 删除所有知识库（批量操作） | None |
| `delete_knowledge_bases_by_keyword()` | 删除名称包含关键字的知识库 | `keyword` |
| `create_knowledge_bases_with_files()` | 创建多个知识库并向每个库添加文件 | `kb_file_mapping` |

### 📝 笔记 API

| 方法 | 说明 | 参数 |
|--------|-------------|---------|
| `get_notes()` | 获取当前用户的所有笔记及完整详细信息 | None |
| `get_notes_list()` | 获取基本信息的简化笔记列表 | None |
| `create_note()` | 创建具有可选元数据和访问控制的新笔记 | `title, data, meta, access_control` |
| `get_note_by_id()` | 根据ID检索特定笔记 | `note_id` |
| `update_note_by_id()` | 使用新内容或元数据更新现有笔记 | `note_id, title, data, meta, access_control` |
| `delete_note_by_id()` | 根据ID删除笔记 | `note_id` |

### 📊 返回值示例

**聊天操作返回：**
```python
{
    "response": "生成的响应文本",
    "chat_id": "聊天-uuid-字符串",
    "message_id": "消息-uuid-字符串",
    "sources": [...]  # RAG 操作时
}
```

**并行聊天返回：**
```python
{
    "responses": {
        "model-1": "模型 1 的响应",
        "model-2": "模型 2 的响应"
    },
    "chat_id": "聊天-uuid-字符串",
    "message_ids": {
        "model-1": "消息-uuid-1",
        "model-2": "消息-uuid-2"
    }
}
```

**知识库/笔记返回：**
```python
{
    "id": "资源-uuid",
    "name": "资源名称",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    ...
}
```

---
