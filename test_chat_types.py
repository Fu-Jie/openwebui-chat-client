#!/usr/bin/env python3
"""
Test script for Chat module type definitions.

Validates that all TypedDict definitions are properly imported and usable.
"""

from openwebui_chat_client.modules.chat.types import (
    MessageDict,
    ChatHistoryDict,
    ChatBodyDict,
    ChatDict,
    ChatFormDict,
    CompletionPayloadDict,
    CompletedPayloadDict,
    MetadataDict,
    ResponseDict,
    ChoiceDict,
    FileDict,
    KnowledgeDict,
    ToolCallDict,
    FunctionCallDict,
    ToolResultDict,
    TagDict,
    FolderDict,
    BackgroundTaskResultDict,
    WorkflowResultDict,
    # Type aliases
    MessageContent,
    MessageRole,
    FinishReason,
    ChatID,
    MessageID,
    FileID,
    KnowledgeID,
    FolderID,
    SessionID,
)

from openwebui_chat_client.modules.chat.payloads import ChatPayloads
from openwebui_chat_client.modules.chat.api import ChatAPI
import uuid


def test_message_dict():
    """Test MessageDict construction."""
    message: MessageDict = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": "Hello, world!",
        "timestamp": 1234567890,
        "childrenIds": [],
    }
    print(f"✅ MessageDict: {message['role']} - {message['content'][:20]}")


def test_chat_history_dict():
    """Test ChatHistoryDict construction."""
    msg_id = str(uuid.uuid4())
    message: MessageDict = {
        "id": msg_id,
        "role": "user",
        "content": "Test message",
        "timestamp": 1234567890,
        "childrenIds": [],
    }

    history: ChatHistoryDict = {
        "currentId": msg_id,
        "messages": {msg_id: message},
    }
    print(f"✅ ChatHistoryDict: currentId={history['currentId']}")


def test_chat_body_dict():
    """Test ChatBodyDict construction."""
    msg_id = str(uuid.uuid4())
    message: MessageDict = {
        "id": msg_id,
        "role": "user",
        "content": "Test",
        "timestamp": 1234567890,
        "childrenIds": [],
    }

    history: ChatHistoryDict = {
        "currentId": msg_id,
        "messages": {msg_id: message},
    }

    chat_body: ChatBodyDict = {
        "title": "Test Chat",
        "history": history,
        "models": ["gpt-4.1"],
    }
    print(f"✅ ChatBodyDict: {chat_body['title']}")


def test_completion_payload_dict():
    """Test CompletionPayloadDict construction."""
    payload: CompletionPayloadDict = {
        "model": "gpt-4.1",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
        "temperature": 0.7,
    }
    print(
        f"✅ CompletionPayloadDict: model={payload['model']}, stream={payload['stream']}"
    )


def test_metadata_dict():
    """Test MetadataDict construction."""
    metadata: MetadataDict = {
        "chat_id": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "session_id": "session_123",
        "tool_ids": ["tool_1", "tool_2"],
    }
    print(f"✅ MetadataDict: chat_id={metadata['chat_id'][:8]}...")


def test_workflow_result_dict():
    """Test WorkflowResultDict construction."""
    result: WorkflowResultDict = {
        "success": True,
        "chat_id": str(uuid.uuid4()),
        "metadata": {
            "chat_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
        },
        "user_message": {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "Test",
            "timestamp": 1234567890,
            "childrenIds": [],
        },
    }
    print(f"✅ WorkflowResultDict: success={result['success']}")


def test_type_aliases():
    """Test type aliases."""
    chat_id: ChatID = str(uuid.uuid4())
    message_id: MessageID = str(uuid.uuid4())
    session_id: SessionID = "session_123"

    print(f"✅ Type aliases: ChatID={chat_id[:8]}..., MessageID={message_id[:8]}...")


def test_payloads_builder():
    """Test ChatPayloads builder methods."""
    # Build user message
    user_msg = ChatPayloads.build_user_message(
        content="Hello, AI!",
        model="gpt-4.1",
    )
    print(
        f"✅ ChatPayloads.build_user_message: {user_msg['role']} - {user_msg['content']}"
    )

    # Build assistant message
    assistant_msg = ChatPayloads.build_assistant_message(
        content="Hello, human!",
        model="gpt-4.1",
        parent_id=user_msg["id"],
    )
    print(
        f"✅ ChatPayloads.build_assistant_message: {assistant_msg['role']} - {assistant_msg['content']}"
    )

    # Build chat history
    history = ChatPayloads.build_chat_history(
        messages=[user_msg, assistant_msg],
        current_id=assistant_msg["id"],
    )
    print(f"✅ ChatPayloads.build_chat_history: {len(history['messages'])} messages")

    # Build completion payload
    completion = ChatPayloads.build_completion_payload(
        model="gpt-4.1",
        messages=[user_msg],
        stream=False,
    )
    print(f"✅ ChatPayloads.build_completion_payload: model={completion['model']}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Chat Module Type Definitions")
    print("=" * 60)
    print()

    test_message_dict()
    test_chat_history_dict()
    test_chat_body_dict()
    test_completion_payload_dict()
    test_metadata_dict()
    test_workflow_result_dict()
    test_type_aliases()
    test_payloads_builder()

    print()
    print("=" * 60)
    print("✅ All type definition tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
