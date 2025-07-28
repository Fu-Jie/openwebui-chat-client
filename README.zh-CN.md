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

---

## 🔑 如何获取你的 API 密钥

1. 登录你的 Open WebUI 账户。
2. 点击左下角的个人资料图片/名称，然后进入 **设置**。
3. 在设置菜单中，导航到 **账户** 部分。
4. 找到 **API 密钥** 区域并 **创建新密钥**。
5. 复制生成的密钥，并将其设置为你的 `OUI_AUTH_TOKEN` 环境变量，或直接在客户端代码中使用。

---

## 📚 API 参考

| 方法 | 说明 | 示例 |
|--------|-------------|---------|
| `chat()` | 启动/继续单模型对话。返回包含 `response`, `chat_id`, `message_id` 的字典。 | `client.chat(question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids)` |
| `stream_chat()` | 启动/继续单模型流式对话，支持实时更新。生成内容块并在结束时返回完整响应/来源。 | `client.stream_chat(question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling)` |
| `chat()` | 启动/继续单模型对话。返回包含 `response`, `chat_id`, `message_id` 的字典。支持追问生成选项。 | `client.chat(question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling)` |
| `parallel_chat()` | 启动/继续多模型对话。返回包含 `responses`, `chat_id`, `message_ids` 的字典。支持追问生成选项。 | `client.parallel_chat(question, chat_title, model_ids, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids, enable_follow_up, enable_auto_tagging, enable_auto_titling)` |
| `update_chat_metadata()` | 为现有对话重新生成和更新标签和/或标题。 | `client.update_chat_metadata(chat_id, regenerate_tags=True, regenerate_title=True)` |
| `rename_chat()` | 聊天重命名 | `client.rename_chat(chat_id, "新标题")` |
| `set_chat_tags()` | 聊天打标签 | `client.set_chat_tags(chat_id, ["tag1"])` |
| `create_folder()` | 创建聊天文件夹 | `client.create_folder("ProjectX")` |
| `list_models()` | 列出所有模型条目（现已提高可靠性） | `client.list_models()` |
| `list_base_models()` | 列出所有基础模型（现已提高可靠性） | `client.list_base_models()` |
| `get_model()` | 获取指定模型详情。当模型不存在且 API 返回 401 时，自动尝试创建模型并重试获取。 | `client.get_model("id")` |
| `create_model()` | 创建自定义模型 | `client.create_model(...)` |
| `update_model()` | 更新模型参数 | `client.update_model("id", temperature=0.5)` |
| `delete_model()` | 删除模型条目 | `client.delete_model("id")` |
| `create_knowledge_base()`| 创建知识库 | `client.create_knowledge_base("MyKB")` |
| `add_file_to_knowledge_base()`| 向知识库添加文件 | `client.add_file_to_knowledge_base(...)` |
| `get_knowledge_base_by_name()`| 获取知识库 | `client.get_knowledge_base_by_name("MyKB")` |
| `delete_knowledge_base()` | 根据ID删除知识库。 | `client.delete_knowledge_base("kb_id")` |
| `delete_all_knowledge_bases()` | 删除所有知识库。 | `client.delete_all_knowledge_bases()` |
| `delete_knowledge_bases_by_keyword()` | 根据关键字删除知识库。 | `client.delete_knowledge_bases_by_keyword("关键字")` |
| `create_knowledge_bases_with_files()` | 批量创建知识库并添加文件。 | `client.create_knowledge_bases_with_files({"KB1": ["file1.txt"]})` |
| `switch_chat_model()` | 切换现有聊天的模型 | `client.switch_chat_model(chat_id, "new-model-id")` |

---
