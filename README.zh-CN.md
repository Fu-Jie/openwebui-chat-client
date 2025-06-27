# OpenWebUI Python 客户端

[English](./README.md) | [简体中文](./README.zh-CN.md)

[![PyPI 版本](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![许可证: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![支持的 Python 版本](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

**openwebui-chat-client** 是面向 [Open WebUI](https://github.com/open-webui/open-webui) API 的状态化 Python 客户端库，支持单/多模型对话、工具调用、文件上传、RAG、知识库管理和高级聊天组织。

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

response, chat_id = client.chat(
    question="你好，你怎么样？",
    chat_title="我的第一次聊天"
)
print(f"回复: {response}")
print(f"Chat ID: {chat_id}")
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
- 智能缓存 & 完善日志

---

## 🧑‍💻 基本示例

### 单模型对话

```python
response, chat_id = client.chat(
    question="介绍一下 OpenAI GPT-4.1 的主要功能？",
    chat_title="GPT-4.1 功能演示"
)
print(response)
```

### 并行模型对话

```python
responses = client.parallel_chat(
    question="比较 GPT-4.1 和 Gemini 2.5 Flash 在文档摘要方面的优势。",
    chat_title="模型对比",
    model_ids=["gpt-4.1", "gemini-2.5-flash"]
)
for m, r in responses.items():
    print(m, r)
```

### 同一会话中切换模型

```python
chat_title = "模型切换演示"
resp1, _ = client.chat(question="你是谁？", chat_title=chat_title, model_id="gpt-4.1")
resp2, _ = client.chat(question="同样的问题，换种风格回答。", chat_title=chat_title, model_id="gemini-2.5-flash")
```

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
response, _ = client.chat(
    question="总结一下手册。",
    chat_title="手册摘要",
    rag_collections=["Doc-KB"]
)
```

### 聊天组织

```python
folder_id = client.create_folder("ProjectX")
client.move_chat_to_folder(chat_id, folder_id)
client.set_chat_tags(chat_id, ["tag1", "tag2"])
client.rename_chat(chat_id, "新标题")
```

---

## API 参考

| 方法 | 说明 | 示例 |
|--------|-------------|---------|
| `chat()` | 启动/继续单模型对话，返回 `(response, chat_id)` | `client.chat(question, chat_title, model_id, image_paths, tool_ids)` |
| `parallel_chat()` | 启动/继续多模型对话，返回 `(responses, chat_id)` | `client.parallel_chat(question, chat_title, model_ids, image_paths, tool_ids)` |
| `rename_chat()` | 聊天重命名 | `client.rename_chat(chat_id, "新标题")` |
| `set_chat_tags()` | 聊天打标签 | `client.set_chat_tags(chat_id, ["tag1"])` |
| `create_folder()` | 创建聊天文件夹 | `client.create_folder("ProjectX")` |
| `list_models()` | 列出所有模型条目 | `client.list_models()` |
| `list_base_models()` | 列出所有基础模型 | `client.list_base_models()` |
| `get_model()` | 获取指定模型详情 | `client.get_model("id")` |
| `create_model()` | 创建自定义模型 | `client.create_model(...)` |
| `update_model()` | 更新模型参数 | `client.update_model("id", temperature=0.5)` |
| `delete_model()` | 删除模型条目 | `client.delete_model("id")` |
| `create_knowledge_base()`| 创建知识库 | `client.create_knowledge_base("MyKB")` |
| `add_file_to_knowledge_base()`| 向知识库添加文件 | `client.add_file_to_knowledge_base(...)` |
| `get_knowledge_base_by_name()`| 获取知识库 | `client.get_knowledge_base_by_name("MyKB")` |

---

## 高级功能

- `image_paths`：传入图片路径，模型支持图文混合对话
- `tool_ids`：传入工具 ID 列表，调用服务器端工具

---

## 发布记录

详见 `CHANGELOG.md`。
