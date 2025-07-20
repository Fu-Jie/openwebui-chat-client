# OpenWebUI Python 客户端

[English](./README.md) | [简体中文](./README.zh-CN.md)

[![PyPI 版本](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![更新日志](https://img.shields.io/badge/更新日志-v0.1.9-blue.svg)](./CHANGELOG.md)
[![许可证: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![支持的 Python 版本](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

**openwebui-chat-client** 是面向 [Open WebUI](https://github.com/open-webui/open-webui) API 的状态化 Python 客户端库，支持单/多模型对话、工具调用、文件上传、RAG、知识库管理和高级聊天组织。

> [!IMPORTANT]
> 本项目正处于积极开发阶段，API 可能会在未来版本中发生变化。请查阅最新文档和 [CHANGELOG.md](./CHANGELOG.md) 以获取最新信息。

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

- 多模态对话：文本、图片、文件上传
- 单模型 & 并行模型对话（A/B 测试）
- 工具集成：在对话中调用服务器端工具
- RAG 检索增强：文件/知识库辅助回复
- 知识库管理：创建、更新、查询
- 模型管理：列出、创建、更新、删除
- 聊天组织：重命名、文件夹、标签、搜索

---

## 🧑‍💻 基本示例

### 单模型对话

```python
result = client.chat(
    question="介绍一下 OpenAI GPT-4.1 的主要功能？",
    chat_title="GPT-4.1 功能演示"
)
if result:
    print(result['response'])
```

### 并行模型对话

```python
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

### 模型管理

```python
base_models = client.list_base_models()
client.create_model(
    model_id="creative-writer:latest",
    name="Creative Writer",
    base_model_id=base_models[0]['id'],
    system_prompt="你是一位世界闻名的作家。",
    temperature=0.85,
    tags=["writing"]
)
client.update_model("creative-writer:latest", temperature=0.7)
client.delete_model("creative-writer:latest")
```

### 知识库 & RAG

```python
client.create_knowledge_base("Doc-KB")
client.add_file_to_knowledge_base("manual.pdf", "Doc-KB")
result = client.chat(
    question="总结一下手册。",
    chat_title="手册摘要",
    rag_collections=["Doc-KB"]
)
if result:
    print(result['response'])
```

### 聊天组织

```python
# 假设你已经通过 client.chat 或 client.parallel_chat 获得了一个 chat_id
# chat_id = result['chat_id'] 

folder_id = client.create_folder("ProjectX")
if folder_id and chat_id:
    client.move_chat_to_folder(chat_id, folder_id)
    client.set_chat_tags(chat_id, ["tag1", "tag2"])
    client.rename_chat(chat_id, "新标题")
```

---

## API 参考

| 方法 | 说明 | 示例 |
|--------|-------------|---------|
| `chat()` | 启动/继续单模型对话，返回包含 `response`, `chat_id`, `message_id` 的字典。 | `client.chat(question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids)` |
| `stream_chat()` | 启动/继续单模型流式对话。生成内容块并在结束时返回完整响应/来源。 | `client.stream_chat(question, chat_title, model_id, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids)` |
| `parallel_chat()` | 启动/继续多模型对话，返回包含 `responses`, `chat_id`, `message_ids` 的字典。 | `client.parallel_chat(question, chat_title, model_ids, folder_name, image_paths, tags, rag_files, rag_collections, tool_ids)` |
| `rename_chat()` | 聊天重命名 | `client.rename_chat(chat_id, "新标题")` |
| `set_chat_tags()` | 聊天打标签 | `client.set_chat_tags(chat_id, ["tag1"])` |
| `create_folder()` | 创建聊天文件夹 | `client.create_folder("ProjectX")` |
| `list_models()` | 列出所有模型条目（现已提高可靠性） | `client.list_models()` |
| `list_base_models()` | 列出所有基础模型（现已提高可靠性） | `client.list_base_models()` |
| `list_custom_models()` | 列出所有自定义模型 | `client.list_custom_models()` |
| `get_model()` | 获取指定模型详情 | `client.get_model("id")` |
| `create_model()` | 创建自定义模型 | `client.create_model(...)` |
| `update_model()` | 更新模型参数 | `client.update_model("id", temperature=0.5)` |
| `delete_model()` | 删除模型条目 | `client.delete_model("id")` |
| `switch_chat_model()` | 切换现有聊天的模型 | `client.switch_chat_model(chat_id, "new-model-id")` |
| `create_knowledge_base()`| 创建知识库 | `client.create_knowledge_base("MyKB")` |
| `add_file_to_knowledge_base()`| 向知识库添加文件 | `client.add_file_to_knowledge_base(...)` |
| `get_knowledge_base_by_name()`| 获取知识库 | `client.get_knowledge_base_by_name("MyKB")` |
| `delete_knowledge_base()` | 根据ID删除知识库。 | `client.delete_knowledge_base("kb_id")` |
| `delete_all_knowledge_bases()` | 删除所有知识库。 | `client.delete_all_knowledge_bases()` |
| `delete_knowledge_bases_by_keyword()` | 根据关键字删除知识库。 | `client.delete_knowledge_bases_by_keyword("关键字")` |
| `create_knowledge_bases_with_files()` | 批量创建知识库并添加文件。 | `client.create_knowledge_bases_with_files({"KB1": ["file1.txt"]})` |

---
