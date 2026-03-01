#!/usr/bin/env python3
"""
Parallel Chat with History Tree Integration Test.

This example demonstrates:
1. Using chat_id parameter in both chat() and parallel_chat()
2. Verifying history tree structure (parentId, childrenIds, modelIdx)
3. Continuing conversations in existing chats
4. Multi-model responses with proper tree structure

Features tested:
- chat() with chat_id parameter
- parallel_chat() with chat_id parameter
- History tree structure validation
- modelIdx field in parallel responses
- Proper parentId and childrenIds linking

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_DEFAULT_MODEL (optional)
- Environment variable: OUI_PARALLEL_MODELS (optional, comma-separated)

Usage:
    python examples/chat_features/parallel_chat_with_history.py
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional

# Add the parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv

from openwebui_chat_client import OpenWebUIClient

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
PARALLEL_MODELS_STR = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
PARALLEL_MODELS = [m.strip() for m in PARALLEL_MODELS_STR.split(",") if m.strip()]

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def validate_history_tree(client: OpenWebUIClient, chat_id: str) -> bool:
    """
    Validate the history tree structure.

    Checks:
    - history.messages is a dict
    - Messages have correct parentId, childrenIds
    - currentId points to a valid message
    - Assistant messages have model and modelIdx fields
    """
    print_section("Validating History Tree Structure")

    # Get chat from server
    chat_obj = client.get_chat_by_id(chat_id)
    if not chat_obj:
        logger.error("❌ Failed to retrieve chat from server")
        return False

    chat_data = chat_obj.get("chat", {})
    history = chat_data.get("history", {})
    messages_dict = history.get("messages", {})
    current_id = history.get("currentId")

    logger.info(f"📊 Chat has {len(messages_dict)} messages in history.messages")
    logger.info(f"🎯 currentId: {current_id}")

    # Validation 1: messages should be a dict
    if not isinstance(messages_dict, dict):
        logger.error(f"❌ history.messages is not a dict: {type(messages_dict)}")
        return False
    logger.info("✅ history.messages is a dict")

    # Validation 2: currentId should point to a valid message
    if current_id and current_id not in messages_dict:
        logger.error(f"❌ currentId '{current_id}' not found in messages")
        return False
    logger.info(f"✅ currentId points to valid message")

    # Validation 3: Check tree structure
    for msg_id, msg in messages_dict.items():
        role = msg.get("role")
        parent_id = msg.get("parentId")
        children_ids = msg.get("childrenIds", [])

        # Check parentId references
        if parent_id and parent_id not in messages_dict:
            logger.error(f"❌ Message {msg_id} has invalid parentId: {parent_id}")
            return False

        # Check childrenIds references
        for child_id in children_ids:
            if child_id not in messages_dict:
                logger.error(f"❌ Message {msg_id} has invalid childId: {child_id}")
                return False
            # Verify reverse link
            child_msg = messages_dict[child_id]
            if child_msg.get("parentId") != msg_id:
                logger.error(
                    f"❌ Child {child_id} doesn't point back to parent {msg_id}"
                )
                return False

        # Check assistant messages have model info
        if role == "assistant":
            model = msg.get("model")
            model_idx = msg.get("modelIdx")
            if not model:
                logger.warning(f"⚠️ Assistant message {msg_id} missing 'model' field")
            else:
                logger.info(
                    f"  ✅ Message {msg_id[:8]}... role={role}, model={model}, modelIdx={model_idx}"
                )

    logger.info("✅ All tree structure validations passed")
    return True


def test_chat_with_chat_id():
    """Test chat() method with chat_id parameter."""
    print_section("Test 1: chat() with chat_id parameter")

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return False

    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
    logger.info(f"✅ Client initialized: {BASE_URL}")

    # Step 1: Create initial chat
    logger.info("\n📝 Step 1: Create initial chat")
    result1 = client.chat(
        question="What is the capital of France?", chat_title="History Tree Test"
    )

    if not result1 or not result1.chat_id:
        logger.error("❌ Failed to create initial chat")
        return False

    chat_id = result1.chat_id
    logger.info(f"✅ Created chat with ID: {chat_id[:16]}...")
    logger.info(f"🤖 Response 1: {result1.content[:100]}...")

    # Step 2: Continue in same chat using chat_id
    logger.info("\n📝 Step 2: Continue in same chat using chat_id")
    result2 = client.chat(
        question="What about Germany?", chat_id=chat_id  # Using chat_id directly
    )

    if not result2:
        logger.error("❌ Failed to continue chat")
        return False

    if result2.chat_id != chat_id:
        logger.error(f"❌ chat_id mismatch: {result2.chat_id} != {chat_id}")
        return False

    logger.info(f"✅ Continued in same chat: {chat_id[:16]}...")
    logger.info(f"🤖 Response 2: {result2.content[:100]}...")

    # Step 3: Validate history tree structure
    logger.info("\n📝 Step 3: Validate history tree structure")
    if not validate_history_tree(client, chat_id):
        return False

    # Step 4: Verify message chain
    logger.info("\n📝 Step 4: Verify message chain")
    chat_obj = client.get_chat_by_id(chat_id)
    history = chat_obj.get("chat", {}).get("history", {})
    messages_dict = history.get("messages", {})

    # Should have: user1 -> assistant1 -> user2 -> assistant2
    user_messages = [m for m in messages_dict.values() if m.get("role") == "user"]
    assistant_messages = [
        m for m in messages_dict.values() if m.get("role") == "assistant"
    ]

    logger.info(f"👤 User messages: {len(user_messages)}")
    logger.info(f"🤖 Assistant messages: {len(assistant_messages)}")

    if len(user_messages) < 2 or len(assistant_messages) < 2:
        logger.error("❌ Expected at least 2 user and 2 assistant messages")
        return False

    logger.info("✅ Test 1 PASSED: chat() with chat_id works correctly")
    return True


def test_parallel_chat_with_chat_id():
    """Test parallel_chat() method with chat_id parameter."""
    print_section("Test 2: parallel_chat() with chat_id parameter")

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return False

    if len(PARALLEL_MODELS) < 2:
        logger.error(f"❌ Need at least 2 models, got: {PARALLEL_MODELS}")
        return False

    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
    logger.info(f"✅ Client initialized: {BASE_URL}")

    # Step 1: Create initial chat with single model
    logger.info("\n📝 Step 1: Create initial chat")
    result1 = client.chat(
        question="Tell me about renewable energy.", chat_title="Parallel Chat Test"
    )

    if not result1 or not result1.chat_id:
        logger.error("❌ Failed to create initial chat")
        return False

    chat_id = result1.chat_id
    logger.info(f"✅ Created chat with ID: {chat_id[:16]}...")

    # Step 2: Use parallel_chat in same chat
    logger.info(f"\n📝 Step 2: Use parallel_chat with chat_id")
    logger.info(f"🤖 Querying models: {PARALLEL_MODELS[:2]}")

    result2 = client.parallel_chat(
        question="Compare solar and wind energy.",
        chat_title="Parallel Chat Test",  # Still needed for fallback
        model_ids=PARALLEL_MODELS[:2],
        chat_id=chat_id,  # Using chat_id to continue in same chat
    )

    if not result2:
        logger.error("❌ Failed to execute parallel_chat")
        return False

    logger.info(f"✅ Parallel chat completed")

    # Step 3: Validate responses
    logger.info("\n📝 Step 3: Validate parallel responses")
    if not result2.responses:
        logger.error("❌ No responses in parallel chat result")
        return False

    logger.info(f"📊 Received {len(result2.responses)} responses")
    for model_id, response_data in result2.responses.items():
        content = response_data.get("content", "")
        logger.info(f"  🤖 {model_id}: {content[:60]}...")

    # Step 4: Validate history tree structure
    logger.info("\n📝 Step 4: Validate history tree structure")
    if not validate_history_tree(client, chat_id):
        return False

    # Step 5: Verify modelIdx field
    logger.info("\n📝 Step 5: Verify modelIdx field in parallel responses")
    chat_obj = client.get_chat_by_id(chat_id)
    history = chat_obj.get("chat", {}).get("history", {})
    messages_dict = history.get("messages", {})
    current_id = history.get("currentId")

    # Find the user message for parallel chat
    current_msg = messages_dict.get(current_id)
    if not current_msg:
        logger.error("❌ Current message not found")
        return False

    # Get parent (should be user message for parallel chat)
    parent_id = current_msg.get("parentId")
    if not parent_id:
        logger.error("❌ Current message has no parent")
        return False

    parent_msg = messages_dict.get(parent_id)
    if parent_msg.get("role") != "user":
        # Current is user, so we need to check its children
        parent_msg = current_msg
        parent_id = current_id

    # Get all assistant children
    children_ids = parent_msg.get("childrenIds", [])
    assistant_children = [
        messages_dict[child_id]
        for child_id in children_ids
        if messages_dict[child_id].get("role") == "assistant"
    ]

    logger.info(f"📊 Found {len(assistant_children)} assistant responses")

    model_indices = set()
    for child in assistant_children:
        model = child.get("model")
        model_idx = child.get("modelIdx")
        logger.info(f"  ✅ model={model}, modelIdx={model_idx}")

        if model_idx is not None:
            model_indices.add(model_idx)

    if len(model_indices) < 2:
        logger.error(
            f"❌ Expected at least 2 different modelIdx values, got: {model_indices}"
        )
        return False

    logger.info(f"✅ modelIdx values are properly set: {sorted(model_indices)}")

    # Step 6: Verify tree structure for parallel responses
    logger.info("\n📝 Step 6: Verify parallel response tree structure")

    # All assistant messages should have same parentId
    parent_ids = [child.get("parentId") for child in assistant_children]
    if len(set(parent_ids)) != 1:
        logger.error(f"❌ Assistant messages have different parents: {set(parent_ids)}")
        return False

    logger.info(f"✅ All {len(assistant_children)} responses share same parent")

    # Parent should have all children in childrenIds
    if not all(child["id"] in children_ids for child in assistant_children):
        logger.error("❌ Not all assistants are in parent's childrenIds")
        return False

    logger.info(f"✅ Parent's childrenIds contains all responses")

    logger.info("✅ Test 2 PASSED: parallel_chat() with chat_id works correctly")
    return True


def test_history_tree_navigation():
    """Test history tree navigation and branching."""
    print_section("Test 3: History Tree Navigation")

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return False

    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)

    # Create a chat with multiple messages
    logger.info("\n📝 Step 1: Create chat with conversation")
    result1 = client.chat(question="What is AI?", chat_title="Tree Navigation Test")

    if not result1:
        logger.error("❌ Failed to create chat")
        return False

    chat_id = result1.chat_id

    # Add more messages
    result2 = client.chat(question="What are its applications?", chat_id=chat_id)

    result3 = client.chat(question="What about limitations?", chat_id=chat_id)

    # Validate final tree
    logger.info("\n📝 Step 2: Validate final tree structure")
    if not validate_history_tree(client, chat_id):
        return False

    # Build message chain from currentId to root
    logger.info("\n📝 Step 3: Build message chain from currentId")
    chat_obj = client.get_chat_by_id(chat_id)
    history = chat_obj.get("chat", {}).get("history", {})
    messages_dict = history.get("messages", {})
    current_id = history.get("currentId")

    # Walk back to root
    chain = []
    current = messages_dict.get(current_id)
    while current:
        chain.insert(
            0,
            {
                "id": current["id"][:8],
                "role": current.get("role"),
                "content": current.get("content", "")[:50],
            },
        )
        parent_id = current.get("parentId")
        current = messages_dict.get(parent_id) if parent_id else None

    logger.info(f"📜 Message chain length: {len(chain)}")
    for i, msg in enumerate(chain):
        logger.info(f"  {i+1}. [{msg['role']}] {msg['content']}...")

    if len(chain) < 6:  # At least 3 user + 3 assistant
        logger.error(f"❌ Expected at least 6 messages in chain, got {len(chain)}")
        return False

    logger.info("✅ Test 3 PASSED: History tree navigation works correctly")
    return True


def main():
    """Run all integration tests."""
    print_section("Parallel Chat with History Tree - Integration Tests")

    logger.info(f"🌐 Server: {BASE_URL}")
    logger.info(f"🤖 Default Model: {DEFAULT_MODEL}")
    logger.info(f"🤖 Parallel Models: {PARALLEL_MODELS}")

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("   Set it with: export OUI_AUTH_TOKEN='your_token_here'")
        return 1

    logger.info("🔑 Auth token configured")

    # Run tests
    tests = [
        ("chat() with chat_id", test_chat_with_chat_id),
        ("parallel_chat() with chat_id", test_parallel_chat_with_chat_id),
        ("History tree navigation", test_history_tree_navigation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\n📊 Overall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
