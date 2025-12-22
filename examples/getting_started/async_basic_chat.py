#!/usr/bin/env python3
"""
Async basic chat functionality example for OpenWebUI Chat Client.

This example demonstrates the async version of the client, showing how to use
AsyncOpenWebUIClient for asynchronous chat operations.

Features demonstrated:
- Async client initialization and context management
- Async basic chat messaging
- Async streaming chat responses
- Async model listing
- Concurrent chat operations with asyncio.gather

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/getting_started/async_basic_chat.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from openwebui_chat_client import AsyncOpenWebUIClient
from dotenv import load_dotenv

# Load environment variables from project root .env (if present) and current dir fallback
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
# Optional: Set to 'true' to clean up all chats before running tests
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ensure_env() -> None:
    if not BASE_URL or not AUTH_TOKEN:
        logger.error("❌ Missing required environment variables.")
        logger.error("   Please set OUI_BASE_URL and OUI_AUTH_TOKEN (e.g., via .env).")
        sys.exit(1)


async def async_basic_chat_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate async basic chat functionality."""
    logger.info("💬 Async Basic Chat Example")
    logger.info("=" * 30)

    # Send a simple question using async chat
    result = await client.chat(
        question="What is the capital of Japan?", chat_title="Async Geography Quiz"
    )

    if result and result.get("response"):
        print(f"\n🤖 Response: {result['response']}")

        if result.get("chat_id"):
            logger.info(f"💾 Chat ID: {result['chat_id'][:8]}...")
        return True
    else:
        logger.error("❌ Failed to get response")
        return False


async def async_streaming_chat_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate async streaming chat functionality."""
    logger.info("\n🌊 Async Streaming Chat Example")
    logger.info("=" * 35)

    print("\n🤖 Streaming Response: ", end="", flush=True)

    full_response = ""
    async for chunk in client.stream_chat(
        question="Tell me a short joke about programming",
        chat_title="Async Streaming Demo",
    ):
        print(chunk, end="", flush=True)
        full_response += chunk

    print()  # New line after streaming completes

    if full_response:
        logger.info(f"✅ Received {len(full_response)} characters via streaming")
        return True
    else:
        logger.error("❌ Failed to get streaming response")
        return False


async def async_list_models_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate async model listing."""
    logger.info("\n📋 Async List Models Example")
    logger.info("=" * 35)

    models = await client.list_models()

    if models:
        logger.info(f"✅ Found {len(models)} models")

        # Show first 5 models
        for i, model in enumerate(models[:5]):
            model_id = model.get("id", "Unknown")
            model_name = model.get("name", model_id)
            print(f"   {i+1}. {model_name}")

        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more models")

        return True
    else:
        logger.error("❌ Failed to list models")
        return False


async def async_concurrent_chat_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate concurrent async chat operations using asyncio.gather."""
    logger.info("\n⚡ Async Concurrent Chat Example")
    logger.info("=" * 40)

    # Define multiple questions to ask concurrently
    questions = [
        ("What is 2 + 2?", "Math Quiz 1"),
        ("Name a planet in our solar system", "Astronomy Quiz"),
        ("What color is the sky on a clear day?", "Simple Quiz"),
    ]

    logger.info(f"📤 Sending {len(questions)} questions concurrently...")

    # Create tasks for concurrent execution
    tasks = [client.chat(question=q, chat_title=title) for q, title in questions]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = 0
    for i, (result, (question, _)) in enumerate(zip(results, questions)):
        if isinstance(result, Exception):
            logger.error(f"   ❌ Q{i+1} failed with error: {result}")
        elif result and result.get("response"):
            response = (
                result["response"][:80] + "..."
                if len(result.get("response", "")) > 80
                else result.get("response", "")
            )
            print(f"   ✅ Q{i+1}: {question[:30]}...")
            print(f"      A: {response}")
            success_count += 1
        else:
            logger.warning(f"   ⚠️ Q{i+1} returned no response")

    logger.info(f"🎯 Completed {success_count}/{len(questions)} concurrent requests")
    return success_count > 0


async def async_context_manager_example() -> bool:
    """Demonstrate async context manager usage."""
    logger.info("\n🔒 Async Context Manager Example")
    logger.info("=" * 40)

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN not set - skipping context manager example")
        return False

    # Using async with for automatic resource cleanup
    async with AsyncOpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
        logger.info("✅ Client created using async context manager")

        # Perform a simple operation
        models = await client.list_models()
        if models:
            logger.info(f"✅ Listed {len(models)} models within context")

        # The client will be automatically closed when exiting the context

    logger.info("✅ Client automatically closed after context exit")
    return True


async def async_user_operations_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate async user operations."""
    logger.info("\n👤 Async User Operations Example")
    logger.info("=" * 40)

    try:
        users = await client.get_users(skip=0, limit=5)

        if users:
            logger.info(f"✅ Found {len(users)} users")
            for user in users[:3]:
                user_name = user.get("name", "Unknown")
                user_email = user.get("email", "N/A")
                print(f"   - {user_name} ({user_email})")
            return True
        else:
            logger.warning("⚠️ No users found or insufficient permissions")
            return True  # Not a failure - might be permission issue
    except Exception as e:
        logger.warning(f"⚠️ User operations may require admin permissions: {e}")
        return True  # Not critical for this example


async def async_chat_list_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate async chat listing."""
    logger.info("\n📜 Async Chat List Example")
    logger.info("=" * 35)

    chats = await client.list_chats(page=1)

    if chats is not None:
        logger.info(f"✅ Found {len(chats)} chats on page 1")

        # Show first 5 chats
        for i, chat in enumerate(chats[:5]):
            chat_title = chat.get("title", "Untitled")
            chat_id = chat.get("id", "Unknown")[:8]
            print(f"   {i+1}. {chat_title[:40]}... (ID: {chat_id}...)")

        if len(chats) > 5:
            print(f"   ... and {len(chats) - 5} more chats")

        return True
    else:
        logger.error("❌ Failed to list chats")
        return False


async def main() -> None:
    """Main async function demonstrating async client functionality."""
    logger.info("🚀 AsyncOpenWebUIClient - Async Examples")
    logger.info("=" * 60)
    ensure_env()

    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        sys.exit(1)

    # Client initialization (async version)
    client: Optional[AsyncOpenWebUIClient] = None
    try:
        client = AsyncOpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)

        # Test basic connectivity
        models = await client.list_models()
        if not models:
            logger.error(
                "❌ Failed to list models - connectivity or authentication issue"
            )
            sys.exit(1)
        logger.info(f"✅ Successfully listed {len(models)} models")
        logger.info("✅ Async client initialized successfully")

        # 🧹 Optional: Clean up all existing chats before running tests
        # Enable by setting OUI_CLEANUP_BEFORE_TEST=true
        if CLEANUP_BEFORE_TEST:
            logger.info("🧹 Cleaning up existing chats for clean test environment...")
            cleanup_success = await client.delete_all_chats()
            if cleanup_success:
                logger.info("✅ Test environment cleaned (all previous chats deleted)")
            else:
                logger.warning(
                    "⚠️ Could not clean up previous chats, continuing anyway..."
                )

    except Exception as e:
        logger.error(f"❌ Failed to initialize async client: {e}")
        sys.exit(1)

    # Run async examples and track success
    examples = [
        ("async_basic_chat", async_basic_chat_example),
        ("async_streaming_chat", async_streaming_chat_example),
        ("async_list_models", async_list_models_example),
        ("async_concurrent_chat", async_concurrent_chat_example),
        ("async_chat_list", async_chat_list_example),
        ("async_user_operations", async_user_operations_example),
    ]

    success_count = 0
    try:
        for example_name, example_func in examples:
            try:
                if await example_func(client):
                    success_count += 1
                    logger.info(f"✅ {example_name} example completed successfully")
                else:
                    logger.error(f"❌ {example_name} example failed")
            except Exception as e:
                logger.error(f"❌ {example_name} example failed with exception: {e}")
                import traceback

                traceback.print_exc()

        # Run standalone context manager example
        logger.info("\n" + "=" * 60)
        if await async_context_manager_example():
            success_count += 1
            logger.info("✅ async_context_manager example completed successfully")

        # Summary
        total_examples = len(examples) + 1  # +1 for context manager example
        if success_count == 0:
            logger.error("❌ All async examples failed")
            logger.error("This indicates a serious connectivity or functionality issue")
            sys.exit(1)
        elif success_count < 3:
            logger.error(f"❌ Only {success_count}/{total_examples} examples succeeded")
            logger.error(
                "Integration test requires most async features to work properly"
            )
            sys.exit(1)

        logger.info(
            f"\n🎉 Async examples completed successfully: {success_count}/{total_examples}!"
        )
        logger.info(
            "💡 AsyncOpenWebUIClient provides the same features as OpenWebUIClient,"
        )
        logger.info(
            "   but with async/await support for better concurrency and performance."
        )

    finally:
        # Always close the client
        if client:
            await client.close()
            logger.info("🔌 Client connection closed")


if __name__ == "__main__":
    asyncio.run(main())
