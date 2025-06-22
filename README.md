# OpenWebUI Python Client

[![PyPI version](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python Versions](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

**openwebui-chat-client** is a comprehensive, stateful Python client library for the [Open WebUI](https://github.com/open-webui/open-webui) API. It enables intelligent interaction with Open WebUI, supporting single/multi-model chats, file uploads, Retrieval-Augmented Generation (RAG), knowledge base management, and advanced chat organization features.

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

response, message_id = client.chat(
    question="Hello, how are you?",
    chat_title="My First Chat"
)

print(response)
```

---

## ✨ Features

- **Multi-Modal Conversations**: Text, images, and file uploads.
- **Single & Parallel Model Chats**: Query one or multiple models simultaneously (great for model A/B tests!).
- **RAG Integration**: Use files or knowledge bases for retrieval-augmented responses.
- **Knowledge Base Management**: Create, update, and use knowledge bases.
- **Model Management**: List, create, update, and delete custom model entries.
- **Chat Organization**: Folders, tags, and search functionality.
- **Smart Caching**: Session, file upload, and knowledge base caches for efficiency.
- **Concurrent Processing**: Parallel model querying for fast multi-model responses.
- **Comprehensive Logging & Error Handling**: Robust and debuggable.

---

## 🧑‍💻 Example: Single Model Chat (`gpt-4.1`)

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

response, message_id = client.chat(
    question="What are the key features of OpenAI GPT-4.1?",
    chat_title="Model Features - GPT-4.1"
)

print("GPT-4.1 Response:", response)
```

---

## 🤖 Example: Parallel Model Chat (`gpt-4.1` and `gemini-2.5-flash`)

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

responses = client.parallel_chat(
    question="Compare the strengths of GPT-4.1 and Gemini 2.5 Flash for document summarization.",
    chat_title="Model Comparison: Summarization",
    model_ids=["gpt-4.1", "gemini-2.5-flash"]
)

for model, resp in responses.items():
    print(f"{model} Response:\n{resp}\n")
```

---

## 🖥️ Example: Page Rendering (Web UI Integration)

After running the above Python code, you can view the conversation and model comparison results in the Open WebUI web interface:

- **Single Model** (`gpt-4.1`):  
  The chat history will display your input question and the GPT-4.1 model's response in the conversational timeline.  
  ![Single Model Chat Example](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/single-model-chat.png)

- **Parallel Models** (`gpt-4.1` & `gemini-2.5-flash`):  
  The chat will show a side-by-side (or grouped) comparison of the responses from both models to the same input, often tagged or color-coded by model.  
  ![Parallel Model Comparison Example](https://cdn.jsdelivr.net/gh/Fu-Jie/openwebui-chat-client@main/examples/images/parallel-model-chat.png)

> **Tip:**  
> The web UI visually distinguishes responses using the model name. You can expand, collapse, or copy each answer, and also tag, organize, and search your chats directly in the interface.

---

## 🧠 Advanced Usage

### Model Management

Manage custom model entries directly through the client. You can create detailed model profiles, list them, update their parameters, and delete them.

```python
# To create a custom model, you first need a base model ID.
# You can list available base models like this:
print("\nListing available base models...")
base_models = client.list_base_models()
base_model_id_for_creation = None
if base_models:
    # Let's use the first available base model
    base_model_id_for_creation = base_models[0]['id']
    print(f"Found base model '{base_model_id_for_creation}' to create a variant from.")
else:
    print("No base models found. Cannot proceed with custom model creation.")
    # In a real script, you might want to exit or handle this error
    base_model_id_for_creation = "gpt-4.1" # Fallback for example

if base_model_id_for_creation:
    # Create a new, detailed model variant
    print("\nCreating a custom 'Creative Writer' model...")
    created_model = client.create_model(
        model_id="creative-writer:latest",
        name="Creative Writer",
        base_model_id=base_model_id_for_creation,
        system_prompt="You are a world-renowned author. Your writing is evocative and poetic.",
        temperature=0.85,
        description="A model finely-tuned for creative writing tasks.",
        suggestion_prompts=["Write a short story about a lost star.", "Describe a futuristic city."],
        tags=["writing", "creative"],
        capabilities={"vision": True, "web_search": False}
    )
    if created_model:
        print(f"Model '{created_model['name']}' created successfully.")

    # List all available models (including custom ones)
    print("\nListing all available models...")
    models = client.list_models()
    if models:
        for model in models:
            print(f"- {model.get('name')} ({model.get('id')})")

    # Update the model with granular changes
    print("\nUpdating the 'Creative Writer' model...")
    updated_model = client.update_model(
        model_id="creative-writer:latest",
        temperature=0.7,
        description="A model for creative writing with a more balanced temperature.",
        suggestion_prompts=["Write a poem about the sea."] # This will overwrite the previous prompts
    )
    if updated_model:
        print("Model updated successfully.")

    # Delete a model entry
    # Be careful! This action is irreversible.
    print("\nDeleting 'creative-writer:latest'...")
    success = client.delete_model("creative-writer:latest")
    if success:
        print("Model 'creative-writer:latest' deleted successfully.")
```

### Knowledge Base and RAG Example

```python
# Create knowledge base and add documents for RAG
client.create_knowledge_base("Doc-KB")
client.add_file_to_knowledge_base("manual.pdf", "Doc-KB")

response, _ = client.chat(
    question="Summarize the manual in Doc-KB.",
    chat_title="Manual Summary",
    rag_collections=["Doc-KB"],
    model_id="gemini-2.5-flash"
)
print("Gemini-2.5-Flash Response:", response)
```

### Chat Organization with Folder and Tags

```python
response, _ = client.chat(
    question="How can I improve code quality?",
    chat_title="Code Quality Tips",
    model_id="gpt-4.1",
    folder_name="Development",
    tags=["coding", "best-practices"]
)
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
| `chat()` | Single model conversation | See "Single Model Chat" |
| `parallel_chat()` | Multi-model conversation | See "Parallel Model Chat" |
| `list_models()` | List all available model entries. | `client.list_models()` |
| `list_base_models()` | List all available base models. | `client.list_base_models()` |
| `get_model()` | Retrieve details for a specific model entry. | `client.get_model("creative-writer:latest")` |
| `create_model()` | Create a detailed, custom model variant. | `client.create_model(...)` |
| `update_model()` | Update an existing model entry with granular changes. | `client.update_model("id", temperature=0.5)` |
| `delete_model()` | Delete a model entry from the server. | `client.delete_model("creative-writer:latest")` |
| `create_knowledge_base()` | Create new knowledge base | `client.create_knowledge_base("MyKB")` |
| `add_file_to_knowledge_base()` | Add file to knowledge base | `client.add_file_to_knowledge_base("file.pdf", "MyKB")` |
| `get_knowledge_base_by_name()` | Retrieve knowledge base | `client.get_knowledge_base_by_name("MyKB")` |
| `create_folder()` | Create chat folder | `client.create_folder("ProjectX")` |
| `set_chat_tags()` | Apply tags to chat | `client.set_chat_tags(chat_id, ["tag1", "tag2"])` |

---

## 🛠️ Troubleshooting

- **Authentication Errors**: Ensure your bearer token is valid.
- **Model Not Found**: Check model IDs are correct (e.g., `"gpt-4.1"`, `"gemini-2.5-flash"`).
- **File Upload Issues**: Ensure file paths exist and permissions are correct.
- **Web UI Not Updating**: Refresh the page or check server logs for errors.
- **Image Not Displayed**: If you use relative paths for screenshots, make sure the images exist in the correct directory in your repository (e.g. `./examples/images/`).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/Fu-Jie/openwebui-chat-client/issues) or submit a pull request.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.  
See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for more details.

---
