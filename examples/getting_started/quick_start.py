#!/usr/bin/env python3
"""
Quick start guide for OpenWebUI Chat Client.

This example provides a quick tour of the main features of the OpenWebUI Chat Client,
designed to get new users up and running quickly with multiple capabilities.

Features demonstrated:
- Basic chat functionality
- Streaming chat
- Parallel multi-model chat
- RAG with files
- Chat organization (folders, tags)
- Model management basics

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/getting_started/quick_start.py
"""

import logging
import os
import sys
import time

# Add the parent directory to path to import the client and utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from utils.file_helpers import TestContent, TestFileManager

from openwebui_chat_client import OpenWebUIClient

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Parse parallel models
parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
PARALLEL_MODELS = [
    model.strip() for model in parallel_models_str.split(",") if model.strip()
]
# Optional: Set to 'true' to clean up all chats before running tests
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"🎯 {title}")
    print("=" * 70)


def demo_basic_chat(client: OpenWebUIClient) -> None:
    """Demonstrate basic chat functionality."""
    print_section_header("1. Basic Chat")

    logger.info("Sending a simple question...")

    result = client.chat(
        question="What are the top 3 benefits of using AI assistants?",
        chat_title="Quick Start - Basic Chat",
        folder_name="Quick Start Demo",
    )

    if result and result.response:
        print(f"\n🤖 AI Response:\n{result.response}\n")
        logger.info("✅ Basic chat completed successfully")
    else:
        logger.error("❌ Basic chat failed")


def demo_streaming_chat(client: OpenWebUIClient) -> None:
    """Demonstrate streaming chat."""
    print_section_header("2. Streaming Chat")

    logger.info("Starting streaming chat...")
    print("\n🤖 Streaming Response:")
    print("-" * 40)

    try:
        for chunk in client.stream_chat(
            question="Write a brief haiku about technology",
            chat_title="Quick Start - Streaming Chat",
            folder_name="Quick Start Demo",
        ):
            print(chunk, end="", flush=True)

        print("\n" + "-" * 40)
        logger.info("✅ Streaming chat completed successfully")
    except Exception as e:
        logger.error(f"❌ Streaming chat failed: {e}")


def demo_parallel_chat(client: OpenWebUIClient) -> None:
    """Demonstrate parallel multi-model chat."""
    print_section_header("3. Parallel Multi-Model Chat")

    if len(PARALLEL_MODELS) < 2:
        logger.warning("⚠️ Need at least 2 models for parallel chat - skipping")
        return

    logger.info(f"Sending question to {len(PARALLEL_MODELS)} models simultaneously...")

    result = client.parallel_chat(
        question="What is the future of renewable energy?",
        chat_title="Quick Start - Parallel Chat",
        model_ids=PARALLEL_MODELS[:2],  # Use first 2 models
        folder_name="Quick Start Demo",
        tags=["quick-start", "parallel", "energy"],
    )

    if result and result.responses:
        print("\n🤖 Responses from Multiple Models:")
        for model_id, response_data in result.responses.items():
            print(f"\n--- {model_id} ---")
            content = (
                response_data.content
                if hasattr(response_data, "content")
                else response_data.get("content", "No response")
            )
            print(content[:200] + "..." if len(content) > 200 else content)

        logger.info("✅ Parallel chat completed successfully")
    else:
        logger.error("❌ Parallel chat failed")


def demo_rag_chat(client: OpenWebUIClient) -> None:
    """Demonstrate RAG (Retrieval Augmented Generation) with files."""
    print_section_header("4. RAG with File Upload")

    with TestFileManager() as file_manager:
        # Create a test file
        file_path = file_manager.create_test_file(
            "ai_knowledge.txt", TestContent.AI_CONTENT
        )

        if not file_path:
            logger.error("❌ Failed to create test file for RAG demo")
            return

        logger.info("Created test file for RAG demonstration...")

        result = client.chat(
            question="Based on the document, explain what artificial intelligence is and its applications.",
            chat_title="Quick Start - RAG Chat",
            rag_files=[file_path],
            folder_name="Quick Start Demo",
            tags=["quick-start", "rag", "ai"],
        )

        if result and result.response:
            print(f"\n🤖 RAG Response:\n{result.response}\n")
            logger.info("✅ RAG chat completed successfully")
        else:
            logger.error("❌ RAG chat failed")


def demo_chat_organization(client: OpenWebUIClient) -> None:
    """Demonstrate chat organization features."""
    print_section_header("5. Chat Organization")

    logger.info("Creating organized chats with folders and tags...")

    # Create chats in different folders with different tags
    chat_configs = [
        {
            "question": "What are the latest trends in web development?",
            "title": "Web Dev Trends 2024",
            "folder": "Technology",
            "tags": ["web-dev", "trends", "2024"],
        },
        {
            "question": "Explain the basics of machine learning",
            "title": "ML Fundamentals",
            "folder": "Education",
            "tags": ["ml", "education", "fundamentals"],
        },
    ]

    created_chats = []
    for config in chat_configs:
        result = client.chat(
            question=config["question"],
            chat_title=config["title"],
            folder_name=config["folder"],
            tags=config["tags"],
        )

        if result and result.chat_id:
            created_chats.append(
                {
                    "title": config["title"],
                    "folder": config["folder"],
                    "tags": config["tags"],
                    "id": result.chat_id,
                }
            )

    logger.info(f"✅ Created {len(created_chats)} organized chats:")
    for chat in created_chats:
        logger.info(f"   📁 {chat['folder']} / {chat['title']}")
        logger.info(f"      🏷️ Tags: {', '.join(chat['tags'])}")


def demo_model_management(client: OpenWebUIClient) -> None:
    """Demonstrate basic model management."""
    print_section_header("6. Model Management")

    try:
        # List available models
        models = client.list_models()
        if models:
            logger.info(f"✅ Found {len(models)} available models:")
            for i, model in enumerate(models[:5], 1):  # Show first 5
                model_name = model.get("name", "Unknown")
                model_id = model.get("id", "Unknown")
                logger.info(f"   {i}. {model_name} ({model_id})")

            if len(models) > 5:
                logger.info(f"   ... and {len(models) - 5} more models")
        else:
            logger.warning("⚠️ No models found")

        # Get details for the default model
        model_details = client.get_model(DEFAULT_MODEL)
        if model_details:
            logger.info(f"✅ Default model '{DEFAULT_MODEL}' details retrieved")
            logger.info(f"   Name: {model_details.get('name', 'Unknown')}")
        else:
            logger.warning(f"⚠️ Could not get details for model: {DEFAULT_MODEL}")

    except Exception as e:
        logger.error(f"❌ Model management demo failed: {e}")


def print_summary() -> None:
    """Print a summary of what was demonstrated."""
    print_section_header("🎉 Quick Start Complete!")

    print(
        """
Congratulations! You've successfully completed the OpenWebUI Chat Client quick start.

What you've learned:
✅ Basic chat messaging
✅ Real-time streaming responses
✅ Multi-model parallel conversations
✅ RAG (Retrieval Augmented Generation) with files
✅ Chat organization with folders and tags
✅ Model management and discovery

Next Steps:
🔗 Explore more examples:
   • python examples/chat_features/streaming_chat.py
   • python examples/rag_knowledge/file_rag.py
   • python examples/model_management/model_operations.py
   • python examples/notes_api/basic_notes.py

📚 Read the documentation:
   • examples/README.md - Complete examples guide
   • ../README.md - Main project documentation

🌐 Join the community:
   • GitHub: https://github.com/Fu-Jie/openwebui-chat-client
   • Issues: Report bugs or request features

Happy coding with OpenWebUI Chat Client! 🚀
"""
    )


def main() -> None:
    """Main function running the quick start guide."""
    print("🚀 OpenWebUI Chat Client - Quick Start Guide")
    print("=" * 60)
    print("Welcome! This guide will walk you through the main features.")

    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("\n🛠️  Setup Required:")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        logger.error("\n💡 For complete setup instructions, run:")
        logger.error("  python examples/config/environment_setup.py")
        return

    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ OpenWebUI Chat Client initialized successfully")
        logger.info(f"   Server: {BASE_URL}")
        logger.info(f"   Default Model: {DEFAULT_MODEL}")

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
        logger.error("\n💡 Check your connection and token, or run:")
        logger.error("  python examples/config/environment_setup.py")
        sys.exit(1)

    # Run quick start demos
    try:
        demo_basic_chat(client)
        time.sleep(1)  # Brief pause between demos

        demo_streaming_chat(client)
        time.sleep(1)

        demo_parallel_chat(client)
        time.sleep(1)

        demo_rag_chat(client)
        time.sleep(1)

        demo_chat_organization(client)
        time.sleep(1)

        demo_model_management(client)

        print_summary()

    except Exception as e:
        logger.error(f"❌ Quick start guide failed: {e}")
        logger.error("💡 Try running individual examples for more specific debugging")
        sys.exit(1)


if __name__ == "__main__":
    main()
