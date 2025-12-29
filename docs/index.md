# OpenWebUI Chat Client

[![PyPI version](https://img.shields.io/pypi/v/openwebui-chat-client?style=flat-square&color=brightgreen)](https://pypi.org/project/openwebui-chat-client/)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-34D058?style=flat-square)](https://www.python.org/downloads/)
[![PyPI Downloads](https://static.pepy.tech/badge/openwebui-chat-client)](https://pepy.tech/projects/openwebui-chat-client)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html)

**openwebui-chat-client** is a comprehensive, stateful Python client library for the [Open WebUI](https://github.com/open-webui/open-webui) API. It enables intelligent interaction with Open WebUI, supporting single/multi-model chats, tool usage, file uploads, Retrieval-Augmented Generation (RAG), knowledge base management, and advanced chat organization features.

---

## ✨ Key Features

- **Autonomous Task Processing**: Multi-step iterative problem-solving with `process_task` and `stream_process_task` methods
- **Automatic Metadata Generation**: Auto-generate tags and titles for your conversations
- **Real-time Streaming Chat**: Experience typewriter-effect real-time content updates
- **Multi-Modal Conversations**: Support for text, images, and file uploads
- **Single & Parallel Model Chats**: Query one or multiple models simultaneously
- **Tool Integration**: Use server-side tools (functions) in your chat requests
- **RAG Integration**: Use files or knowledge bases for retrieval-augmented responses
- **Knowledge Base Management**: Create, update, and use knowledge bases
- **Notes & Prompts Management**: Full CRUD operations for notes and prompts
- **Model Management**: List, create, update, and delete custom model entries
- **Async Support**: Full async client support for high-performance applications

---

## ⚡ Quick Start

### Installation

```bash
pip install openwebui-chat-client
```

### Hello World Example

```python
from openwebui_chat_client import OpenWebUIClient
import logging

logging.basicConfig(level=logging.INFO)

# Initialize the client
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# Send a chat message
result = client.chat(
    question="Hello, how are you?",
    chat_title="My First Chat"
)

if result:
    print(f"Response: {result['response']}")
    print(f"Chat ID: {result['chat_id']}")
```

### Async Example

For asynchronous applications (e.g., FastAPI, Sanic), use the `AsyncOpenWebUIClient`:

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
        question="Hello from async!",
        chat_title="Async Chat"
    )

    if result:
        print(f"Response: {result['response']}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔑 Getting Your API Key

1. Log in to your Open WebUI account
2. Click on your profile picture/name in the bottom-left corner and go to **Settings**
3. Navigate to the **Account** section
4. Find the **API Keys** area and **Create a new key**
5. Copy the generated key and use it as your `token`

---

## 📚 Documentation

- [Installation Guide](installation.md) - Detailed installation instructions
- [User Guide](usage.md) - Comprehensive usage examples and advanced features
- [API Reference](api.md) - Complete API documentation

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/Fu-Jie/openwebui-chat-client/issues) or submit a pull request.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.  
See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for more details.
