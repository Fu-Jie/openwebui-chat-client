#!/usr/bin/env python3
"""
Streaming chat example for OpenWebUI Chat Client.

This example demonstrates real-time streaming chat functionality, where responses
are received and displayed incrementally as they are generated.

Features demonstrated:
- Real-time streaming chat responses
- Streaming with follow-up suggestions
- Streaming with image inputs (multimodal)
- Error handling in streaming scenarios

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/chat_features/streaming_chat.py
"""

import logging
import os
import sys

# Add the parent directory to path to import the client and utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from utils.file_helpers import TestFileManager

from openwebui_chat_client import OpenWebUIClient

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
MULTIMODAL_MODEL = os.getenv("OUI_MULTIMODAL_MODEL", DEFAULT_MODEL)
# Optional: Set to 'true' to clean up all chats before running tests
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def basic_streaming_example(client: OpenWebUIClient) -> None:
    """Demonstrate basic streaming chat functionality."""
    logger.info("📡 Basic Streaming Chat Example")
    logger.info("=" * 40)

    question = "Write a short poem about artificial intelligence"
    chat_title = "AI Poetry Streaming"

    logger.info(f"🎯 Question: {question}")
    logger.info("💭 Streaming response:")

    print("\n" + "=" * 50)
    print("🤖 AI Response (Streaming):")
    print("=" * 50)

    try:
        # Stream the response
        for chunk in client.stream_chat(
            question=question, chat_title=chat_title, model_id=DEFAULT_MODEL
        ):
            print(chunk, end="", flush=True)

        print("\n" + "=" * 50)
        logger.info("✅ Streaming completed successfully")

    except Exception as e:
        logger.error(f"❌ Streaming failed: {e}")


def streaming_with_follow_up_example(client: OpenWebUIClient) -> None:
    """Demonstrate streaming with follow-up suggestions."""
    logger.info("\n🔄 Streaming with Follow-up Suggestions")
    logger.info("=" * 50)

    question = "Explain the concept of machine learning"
    chat_title = "ML Explanation Streaming"

    logger.info(f"🎯 Question: {question}")
    logger.info("💭 Streaming response with follow-up suggestions:")

    print("\n" + "=" * 50)
    print("🤖 AI Response (Streaming with Follow-up):")
    print("=" * 50)

    try:
        # Stream with follow-up enabled
        stream_gen = client.stream_chat(
            question=question, chat_title=chat_title, enable_follow_up=True
        )

        # Process streaming chunks and capture return value
        chat_response = None
        while True:
            try:
                chunk = next(stream_gen)
                print(chunk, end="", flush=True)
            except StopIteration as e:
                # The return value of the generator is available in e.value
                chat_response = e.value
                break

        print("\n" + "=" * 50)

        if chat_response and chat_response.follow_ups:
            logger.info("🤔 Follow-up suggestions received:")
            for i, suggestion in enumerate(chat_response.follow_ups, 1):
                print(f"  {i}. {suggestion}")
        else:
            logger.info("ℹ️ No follow-up suggestions generated")

        logger.info("✅ Streaming with follow-up completed")

    except Exception as e:
        logger.error(f"❌ Streaming with follow-up failed: {e}")


def streaming_with_image_example(client: OpenWebUIClient) -> None:
    """Demonstrate streaming chat with image input."""
    logger.info("\n🖼️ Streaming Chat with Image Input")
    logger.info("=" * 45)

    # Create a test image
    with TestFileManager() as file_manager:
        image_path = file_manager.create_test_file(
            "streaming_test.png", "Streaming Chat Test Image", "image"
        )

        if not image_path:
            logger.warning("⚠️ Could not create test image - skipping this example")
            return

        question = "What do you see in this image? Describe it in detail."
        chat_title = "Image Description Streaming"

        logger.info(f"🎯 Question: {question}")
        logger.info(f"🖼️ Image: {image_path}")
        logger.info("💭 Streaming response:")

        print("\n" + "=" * 50)
        print("🤖 AI Response (Streaming with Image):")
        print("=" * 50)

        try:
            # Stream with image input
            for chunk in client.stream_chat(
                question=question,
                chat_title=chat_title,
                image_paths=[image_path],
                model_id=MULTIMODAL_MODEL,
            ):
                print(chunk, end="", flush=True)

            print("\n" + "=" * 50)
            logger.info("✅ Streaming with image completed successfully")

        except Exception as e:
            logger.error(f"❌ Streaming with image failed: {e}")


def streaming_error_handling_example(client: OpenWebUIClient) -> None:
    """Demonstrate error handling in streaming scenarios."""
    logger.info("\n⚠️ Streaming Error Handling Example")
    logger.info("=" * 45)

    # Test with an intentionally problematic request
    question = "x" * 10000  # Very long question that might cause issues
    chat_title = "Error Handling Test"

    logger.info("🧪 Testing error handling with problematic input")

    try:
        # Attempt to stream with problematic input
        response_chunks = []
        for chunk in client.stream_chat(
            question=question,
            chat_title=chat_title,
            model_id="non-existent-model",  # This should cause an error
        ):
            response_chunks.append(chunk)
            if len(response_chunks) > 10:  # Limit output for demonstration
                break

        if response_chunks:
            logger.info("🤔 Unexpectedly received response chunks")
        else:
            logger.info("ℹ️ No response chunks received")

    except Exception as e:
        logger.info(f"✅ Error handled correctly: {e}")

    # Test with a valid but simple request to show recovery
    logger.info("🔄 Testing recovery with valid request...")

    try:
        recovery_chunks = []
        for chunk in client.stream_chat(
            question="Hello, are you working?",
            chat_title="Recovery Test",
            model_id=DEFAULT_MODEL,
        ):
            recovery_chunks.append(chunk)
            if len(recovery_chunks) > 5:  # Just get a few chunks
                break

        if recovery_chunks:
            logger.info(
                f"✅ Successfully recovered - received {len(recovery_chunks)} chunks"
            )
        else:
            logger.warning("⚠️ Recovery failed - no chunks received")

    except Exception as e:
        logger.error(f"❌ Recovery failed: {e}")


def main() -> None:
    """Main function demonstrating streaming chat functionality."""
    logger.info("🚀 OpenWebUI Chat Client - Streaming Chat Examples")
    logger.info("=" * 65)

    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        return

    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")

        # 🧹 Optional: Clean up all existing chats before running tests
        # Enable by setting OUI_CLEANUP_BEFORE_TEST=true
        if CLEANUP_BEFORE_TEST:
            logger.info("🧹 Cleaning up existing chats for clean test environment...")
            cleanup_success = client.delete_all_chats()
            if cleanup_success:
                logger.info("✅ Test environment cleaned (all previous chats deleted)")
            else:
                logger.warning(
                    "⚠️ Could not clean up previous chats, continuing anyway..."
                )

    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)

    # Run streaming examples
    try:
        basic_streaming_example(client)
        streaming_with_follow_up_example(client)
        streaming_with_image_example(client)
        streaming_error_handling_example(client)

        logger.info("\n🎉 Streaming chat examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/chat_features/parallel_chat.py")
        logger.info(
            "   - Try: python examples/advanced_features/real_time_streaming.py"
        )

    except Exception as e:
        logger.error(f"❌ Streaming chat examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
