# OpenWebUI Python Client

[![PyPI version](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python Versions](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

**openwebui-chat-client** is a comprehensive, stateful Python client library for the [Open WebUI](https://github.com/open-webui/open-webui) API. It enables intelligent interaction with Open WebUI, supporting single/multi-model chats, tool usage, file uploads, Retrieval-Augmented Generation (RAG), knowledge base management, and advanced chat organization features.

---

## 🚀 Installation

Install the client directly from PyPI:

```bash
pip install openwebui-chat-client
```

---

## ⚡ Quick Start

```python
from openwebui_chat_client import OpenWebUIClient
import logging

logging.basicConfig(level=logging.INFO)

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# The chat method returns the response and the chat_id
response, chat_id = client.chat(
    question="Hello, how are you?",
    chat_title="My First Chat"
)

print(f"Response: {response}")
print(f"Chat ID: {chat_id}")
```

---

## ✨ Features

- **Multi-Modal Conversations**: Text, images, and file uploads.
- **Single & Parallel Model Chats**: Query one or multiple models simultaneously.
- **Tool Integration**: Use server-side tools (functions) in your chat requests.
- **RAG Integration**: Use files or knowledge bases for retrieval-augmented responses.
- **Knowledge Base Management**: Create, update, and use knowledge bases.
- **Model Management**: List, create, update, and delete custom model entries.
- **Chat Organization**: Rename chats, use folders, tags, and search functionality.
- **Smart Caching**: Session, file upload, and knowledge base caches for efficiency.
- **Concurrent Processing**: Parallel model querying for fast multi-model responses.
- **Comprehensive Logging & Error Handling**: Robust and debuggable.

---

## 🧑‍💻 Basic Examples

### Single Model Chat

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

response, chat_id = client.chat(
    question="What are the key features of OpenAI's GPT-4.1?",
    chat_title="Model Features - GPT-4.1"
)

print("GPT-4.1 Response:", response)
```

### Parallel Model Chat

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

responses, chat_id = client.parallel_chat(
    question="Compare the strengths of GPT-4.1 and Gemini 2.5 Flash for document summarization.",
    chat_title="Model Comparison: Summarization",
    model_ids=["gpt-4.1", "gemini-2.5-flash"]
)

if responses:
    for model, resp in responses.items():
        print(f"{model} Response:\n{resp}\n")
```

---

## 🧠 Advanced Chat Examples

### 1. Using Tools (Functions)

If you have tools configured in your Open WebUI instance (like a weather tool or a web search tool), you can specify which ones to use in a request.

```python
# Assumes you have a tool with the ID 'search-the-web-tool' configured on your server.
# This tool would need to be created in the Open WebUI "Tools" section.

response, chat_id = client.chat(
    question="What are the latest developments in AI regulation in the EU?",
    chat_title="AI Regulation News",
    model_id="gpt-4.1",
    tool_ids=["search-the-web-tool"] # Pass the ID of the tool to use
)

print(response)
```

### 2. Multimodal Chat (with Images)

Send images along with your text prompt to a vision-capable model.

```python
# Make sure 'chart.png' exists in the same directory as your script.
# The model 'gpt-4.1' is vision-capable.

response, chat_id = client.chat(
    question="Please analyze the attached sales chart and provide a summary of the trends.",
    chat_title="Sales Chart Analysis",
    model_id="gpt-4.1",
    image_paths=["./chart.png"] # A list of local file paths to your images
)

print(response)
```

### 3. Switching Models in the Same Chat

You can start a conversation with one model and then switch to another for a subsequent question, all within the same chat history. The client handles the state seamlessly.

```python
# Start a chat with a powerful general-purpose model
response_1, chat_id_1 = client.chat(
    question="Explain the theory of relativity in simple terms.",
    chat_title="Science and Speed",
    model_id="gpt-4.1"
)
print(f"GPT-4.1 answered: {response_1}")

# Now, ask a different question in the SAME chat, but switch to a fast, efficient model
response_2, chat_id_2 = client.chat(
    question="Now, what are the top 3 fastest land animals?",
    chat_title="Science and Speed",   # Use the same title to continue the chat
    model_id="gemini-2.5-flash"  # Switch to a different model
)
print(f"\nGemini 2.5 Flash answered: {response_2}")

# Both chat_id_1 and chat_id_2 will be the same, as it's the same conversation.
print(f"\nChat ID for both interactions: {chat_id_1}")
```

---

## 🔑 How to get your API Key

1. Log in to your Open WebUI account.
2. Click on your profile picture/name in the bottom-left corner and go to **Settings**.
3. In the settings menu, navigate to the **Account** section.
4. Find the **API Keys** area and **Create a new key**.
5. Copy the generated key and set it as your `OUI_AUTH_TOKEN` environment variable or use it directly in your client code.

---

## 📚 API Reference

| Method | Description | Example |
|--------|-------------|---------|
| `chat()` | Start/continue a single-model conversation. Returns `(response, chat_id)`. | `client.chat(question, chat_title, model_id, image_paths, tool_ids)` |
| `parallel_chat()` | Start/continue a multi-model conversation. Returns `(responses, chat_id)`. | `client.parallel_chat(question, chat_title, model_ids, image_paths, tool_ids)` |
| `rename_chat()` | Rename an existing chat. | `client.rename_chat(chat_id, "New Title")` |
| `set_chat_tags()` | Apply tags to a chat. | `client.set_chat_tags(chat_id, ["tag1"])` |
| `create_folder()` | Create a chat folder. | `client.create_folder("ProjectX")` |
| `list_models()` | List all available model entries. | `client.list_models()` |
| `list_base_models()` | List all available base models. | `client.list_base_models()` |
| `get_model()` | Retrieve details for a specific model entry. | `client.get_model("id")` |
| `create_model()` | Create a detailed, custom model variant. | `client.create_model(...)` |
| `update_model()` | Update an existing model entry with granular changes. | `client.update_model("id", temperature=0.5)` |
| `delete_model()` | Delete a model entry from the server. | `client.delete_model("id")` |
| `create_knowledge_base()`| Create a new knowledge base. | `client.create_knowledge_base("MyKB")` |
| `add_file_to_knowledge_base()`| Add a file to a knowledge base. | `client.add_file_to_knowledge_base(...)` |
| `get_knowledge_base_by_name()`| Retrieve a knowledge base by its name. | `client.get_knowledge_base_by_name("MyKB")` |

---

## 🛠️ Troubleshooting

- **Authentication Errors**: Ensure your bearer token is valid.
- **Model Not Found**: Check that the model IDs are correct (e.g., `"gpt-4.1"`, `"gemini-2.5-flash"`) and available on your Open WebUI instance.
- **Tool Not Found**: Ensure the `tool_ids` you provide match the IDs of tools configured in the Open WebUI settings.
- **File/Image Upload Issues**: Ensure file paths are correct and the application has the necessary permissions to read them.
- **Web UI Not Updating**: Refresh the page or check the server logs for any potential errors.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/Fu-Jie/openwebui-chat-client/issues) or submit a pull request.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.  
See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for more details.

---
