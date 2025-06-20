# openwebui-chat-client

[![PyPI version](https://badge.fury.io/py/openwebui-chat-client.svg)](https://badge.fury.io/py/openwebui-chat-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent, stateful Python client for the [Open WebUI](https://github.com/open-webui/open-webui) API.

**openwebui-chat-client** is designed for developers and automation engineers who need to programmatically interact with Open WebUI. It treats conversations as unique entities identified by their titles, allowing you to robustly create, manage, and continue chats, handle multimodal inputs, and organize your workflows with ease.

## ✨ Features

-   **Global Title Uniqueness**: Manage conversations using a unique title, regardless of their folder location.
-   **Smart Session Continuation**: Automatically finds and continues the most recently updated conversation with a given title, or creates a new one if it doesn't exist.
-   **Dynamic Folder Management**: Automatically creates folders and moves chats to organize your projects, e.g., from "In Progress" to "Completed".
-   **Stateful Client Session**: Caches active conversations within a single client instance to boost performance by avoiding redundant API searches.
-   **Multimodal Support**: Seamlessly send both text and local images in your prompts to multimodal models like LLaVA.
-   **Clean, Object-Oriented Design**: All logic is encapsulated in the `OpenWebUIClient` class for easy integration into your projects.

## 🛠️ Installation

Install the package directly from PyPI:

```bash
pip install openwebui-chat-client
```

## 🚀 Quick Start

First, obtain your API token from your Open WebUI instance.

```python
from openwebui_chat_client import OpenWebUIClient

# 1. Configure your client
#    Ensure the model you choose supports your intended use (e.g., 'llava:latest' for images).
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="YOUR_AUTH_TOKEN",
    default_model_id="llava:latest"
)

# 2. Start or continue a text-based conversation
response, message_id = client.chat(
    question="What are the key principles of object-oriented programming?",
    chat_title="OOP Principles Discussion"
)

if response:
    print(f"AI: {response}")

# 3. Continue the same conversation with an image
#    The client will automatically find the "OOP Principles Discussion" chat.
response, message_id = client.chat(
    question="Can you explain this UML diagram?",
    chat_title="OOP Principles Discussion",
    folder_name="Software Design",  # The chat will be moved here if not already
    image_paths=["./path/to/your/diagram.png"]
)

if response:
    print(f"AI: {response}")
```

### Configuration

-   `base_url`: The URL of your running Open WebUI instance.
-   `token`: Your authentication token. To get it:
    1.  Log in to Open WebUI.
    2.  Open browser developer tools (F12) and go to the "Network" tab.
    3.  Perform any action (e.g., send a message).
    4.  Find a request to the API, go to "Headers", and copy the value from the `Authorization: Bearer <YOUR_TOKEN>` header.
-   `default_model_id`: The model to use for new conversations.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Fu-Jie/openwebui-chat-client/issues).

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.