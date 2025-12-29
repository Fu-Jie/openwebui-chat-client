# OpenWebUI 聊天客户端

[![PyPI version](https://img.shields.io/pypi/v/openwebui-chat-client?style=flat-square&color=brightgreen)](https://pypi.org/project/openwebui-chat-client/)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-34D058?style=flat-square)](https://www.python.org/downloads/)
[![PyPI Downloads](https://static.pepy.tech/badge/openwebui-chat-client)](https://pepy.tech/projects/openwebui-chat-client)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html)

**openwebui-chat-client** 是一个全面的、有状态的 Python 客户端库，用于 [Open WebUI](https://github.com/open-webui/open-webui) API。它支持单/多模型聊天、工具使用、文件上传、检索增强生成（RAG）、知识库管理和高级聊天组织功能。

---

## ✨ 主要特性

- **自主任务处理**: 使用 `process_task` 和 `stream_process_task` 方法进行多步骤迭代问题解决
- **自动元数据生成**: 自动为您的对话生成标签和标题
- **实时流式聊天**: 体验打字机效果的实时内容更新
- **多模态对话**: 支持文本、图像和文件上传
- **单模型和并行模型聊天**: 同时查询一个或多个模型
- **工具集成**: 在聊天请求中使用服务器端工具（函数）
- **RAG 集成**: 使用文件或知识库进行检索增强响应
- **知识库管理**: 创建、更新和使用知识库
- **笔记和提示词管理**: 完整的笔记和提示词 CRUD 操作
- **模型管理**: 列出、创建、更新和删除自定义模型条目
- **异步支持**: 完整的异步客户端支持，适用于高性能应用

---

## ⚡ 快速开始

### 安装

```bash
pip install openwebui-chat-client
```

### Hello World 示例

```python
from openwebui_chat_client import OpenWebUIClient
import logging

logging.basicConfig(level=logging.INFO)

# 初始化客户端
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# 发送聊天消息
result = client.chat(
    question="你好，你好吗？",
    chat_title="我的第一次聊天"
)

if result:
    print(f"响应: {result['response']}")
    print(f"聊天 ID: {result['chat_id']}")
```

### 异步示例

对于异步应用程序（如 FastAPI、Sanic），使用 `AsyncOpenWebUIClient`：

```python
import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient

async def main():
    client = AsyncOpenWebUIClient(
        base_url="http://localhost:3000",
        token="your-bearer-token",
        default_model_id="gpt-4.1"
    )

    result = await client.chat(
        question="异步问候！",
        chat_title="异步聊天"
    )

    if result:
        print(f"响应: {result['response']}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔑 获取 API 密钥

1. 登录您的 Open WebUI 账户
2. 点击左下角的个人头像/名称，进入 **设置**
3. 导航到 **账户** 部分
4. 找到 **API 密钥** 区域并 **创建新密钥**
5. 复制生成的密钥并将其用作 `token`

---

## 📚 文档

- [安装指南](installation.zh.md) - 详细的安装说明
- [用户指南](usage.zh.md) - 完整的使用示例和高级功能
- [API 参考](api.zh.md) - 完整的 API 文档

---

## 🤝 贡献

欢迎贡献、问题和功能请求！
请随时查看 [问题页面](https://github.com/Fu-Jie/openwebui-chat-client/issues) 或提交拉取请求。

---

## 📄 许可证

本项目采用 **GNU 通用公共许可证 v3.0 (GPLv3)** 授权。
详见 [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) 文件。
