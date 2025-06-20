# openwebui-chat-client

[![PyPI version](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/openwebui-chat-client.svg)](https://pypi.org/project/openwebui-chat-client/)

An intelligent, stateful Python client for the [Open WebUI](https://github.com/open-webui/open-webui) API, designed for robust automation and seamless integration.

**openwebui-chat-client** empowers developers and automation engineers to programmatically control the full lifecycle of conversations in Open WebUI. It treats conversations as unique entities identified by their titles, allowing you to reliably create, manage, and continue chats, handle both single and parallel multi-model conversations, process multimodal inputs, and organize your workflows with ease.

---

## ✨ Features

- **Global Title Uniqueness**: Manage conversations using a unique title as a stable identifier.
- **Smart Session Continuation**: Automatically finds and continues existing conversations or creates new ones.
- **Multi-Model Parallel Chat**: Send a single prompt to multiple models simultaneously.
- **Dynamic Folder Management**: Automatically create folders and move chats to manage workflows.
- **Stateful Client Session**: Caches active conversations to boost performance.
- **Multimodal Support**: Send text and local images to multimodal models.
- **Clean, Object-Oriented Design**: Encapsulated in the `OpenWebUIClient` class.
- **Professional Logging**: Uses Python's standard `logging` module.

## 🛠️ Installation

Install the package from PyPI:

```bash
pip install openwebui-chat-client
```

> To install directly from the official PyPI repository, bypassing any local mirrors, use:
> `pip install --index-url https://pypi.org/simple/ openwebui-chat-client`

## 🚀 Quick Start

### 1. Set Environment Variables

For security, it is highly recommended to configure the client using environment variables rather than hardcoding values in your script.

**On Linux or macOS:**

```bash
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your_api_key_from_open_webui"
```

**On Windows (PowerShell):**

```powershell
$env:OUI_BASE_URL="http://localhost:3000"
$env:OUI_AUTH_TOKEN="your_api_key_from_open_webui"
```

### 2. Run the Client

Create a Python file (e.g., `main.py`) with the following code:

```python
import logging
import os
from openwebui_chat_client import OpenWebUIClient

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Load Configuration from Environment ---
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

if not AUTH_TOKEN:
    raise ValueError("OUI_AUTH_TOKEN environment variable not set. Please set it to your API key.")

# --- Initialize and Use the Client ---
client = OpenWebUIClient(
    base_url=BASE_URL,
    token=AUTH_TOKEN,
    default_model_id="gpt-4.1"
)

# Start a multi-model parallel conversation
models_to_query = ["gpt-4.1", "gemini-2.5-flash"]
responses = client.parallel_chat(
    question="What are the top 3 benefits of using Python for data science?",
    chat_title="Python for Data Science",
    model_ids=models_to_query
)

if responses:
    for model, content in responses.items():
        print(f"\n🤖 [{model}'s Response]:\n{content}")
```

### Configuration Details

- `base_url` / `OUI_BASE_URL`: The URL of your running Open WebUI instance.
- `token` / `OUI_AUTH_TOKEN`: Your authentication API key.
- `default_model_id`: The model ID to use for new single-model chats.

**How to get your API Key:**

1. Log in to your Open WebUI account.
2. Click on your profile picture/name in the bottom-left corner and go to **Settings**.
3. In the settings menu, navigate to the **Account** section.
4. Find the **API Keys** area and **Create a new key**.
5. Copy the generated key and set it as your `OUI_AUTH_TOKEN` environment variable.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Fu-Jie/openwebui-chat-client/issues).

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
