# User Guide

This guide covers the main features and usage patterns of the `openwebui-chat-client` library.

---

## Basic Usage

### Initializing the Client

```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4o"
)
```

### Simple Chat

```python
result = client.chat(
    question="What is the capital of France?",
    chat_title="Geography Questions"
)

if result:
    # Use .content or .text to access the response
    print(f"Response: {result.content}")
    print(f"Chat ID: {result.chat_id}")
    print(f"Message ID: {result.message_id}")
```

---

## Chat Features

### Parallel Model Chat

Query multiple models simultaneously and compare their responses:

```python
result = client.parallel_chat(
    question="Explain quantum computing in simple terms.",
    chat_title="AI Model Comparison",
    model_ids=["gpt-4o", "gemini-pro"],
    folder_name="Technical Comparisons"
)

if result and result.responses:
    for model, response in result.responses.items():
        print(f"--- {model} ---")
        print(response.content)
        print()
```

### Streaming Chat

Get real-time responses with a typewriter effect:

```python
stream = client.stream_chat(
    question="Tell me a short story about a robot.",
    chat_title="Creative Writing"
)

for chunk in stream:
    print(chunk, end="", flush=True)
print()  # New line at the end
```

### Triggering Actions & Artifacts Mode

The client can trigger server-side actions (like Mind Maps) and automatically synchronize the RichUI components to the database so they appear in your browser.

```python
# 1. Initiate a chat
result = client.chat(question="Summarize the history of AI.")

# 2. Find available actions
actions = client.get_actions()

# 3. Trigger an action (e.g., a Smart Mind Map)
# The SDK automatically detects the output format (HTML or JSON)
# and performs a surgical sync to trigger the UI Artifacts panel.
action_result = client.trigger_action(
    action_id="smart_mind_map",
    chat_id=result.chat_id,
    message_id=result.message_id
)

if action_result.status:
    print("Action executed and RichUI synchronized!")
```

---

## RAG & Knowledge Base

### Chat with Files

Upload files and use them as context for your questions:

```python
result = client.chat(
    question="Summarize this document for me.",
    chat_title="File Analysis",
    rag_files=["./report.pdf"]
)

if result:
    print(result.content)
    if result.sources:
        print(f"Referenced {len(result.sources)} sources.")
```

### Using Knowledge Bases

Reference existing knowledge base collections in your chat:

```python
result = client.chat(
    question="Based on our internal wiki, how do I reset my password?",
    chat_title="Wiki Search",
    rag_collections=["internal-wiki"]
)
```

---

## Advanced Management

### Folders & Chat Organization

```python
# Create a folder
folder_id = client.create_folder("Research Projects")

# Move chat to folder
client.move_chat_to_folder(chat_id, folder_id)

# Set tags
client.set_chat_tags(chat_id, ["ai", "history", "milestones"])
```

### Async Operations

For high-concurrency environments, use the `AsyncOpenWebUIClient`:

```python
import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient

async def main():
    async with AsyncOpenWebUIClient(base_url=url, token=token) as client:
        result = await client.chat(question="Hello!")
        print(result.content)

asyncio.run(main())
```
