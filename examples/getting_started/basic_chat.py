#!/usr/bin/env python3
"""
Basic chat functionality example for OpenWebUI Chat Client.

This example demonstrates fundamental chat operations including sending messages,
organizing chats with titles and folders, and basic chat management.

Features demonstrated:
- Basic chat messaging
- Chat titles and organization
- Chat folders and tags
- Multiple messages in the same chat
- Chat information retrieval

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/getting_started/basic_chat.py
"""

import logging
import os
import sys
import time
from typing import Optional, Dict, Any

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
# Optional: Set to 'true' to clean up all chats before running tests
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def basic_chat_example(client: OpenWebUIClient) -> bool:
    """Demonstrate basic chat functionality."""
    logger.info("💬 Basic Chat Example")
    logger.info("=" * 30)
    
    # Send a simple question
    result = client.chat(
        question="What is the capital of France?",
        chat_title="Geography Quiz"
    )
    
    if result and result.get("response"):
        print(f"\n🤖 Response: {result['response']}")
        
        if result.get("chat_id"):
            logger.info(f"💾 Chat ID: {result['chat_id'][:8]}...")
        return True
    else:
        logger.error("❌ Failed to get response")
        return False


def organized_chat_example(client: OpenWebUIClient) -> bool:
    """Demonstrate chat organization with folders and tags."""
    logger.info("\n📁 Organized Chat Example")
    logger.info("=" * 35)
    
    # Create a chat with organization
    result = client.chat(
        question="Explain the basics of machine learning in simple terms",
        chat_title="ML Learning Session",
        folder_name="Education",
        tags=["learning", "ai", "basics"]
    )
    
    if result and result.get("response"):
        print(f"\n🤖 Response: {result['response'][:200]}...")
        logger.info("✅ Created organized chat with folder and tags")
        
        if result.get("chat_id"):
            logger.info(f"💾 Chat ID: {result['chat_id'][:8]}...")
            logger.info("📁 Folder: Education")
            logger.info("🏷️ Tags: learning, ai, basics")
        return True
    else:
        logger.error("❌ Failed to create organized chat")
        return False


def multi_message_chat_example(client: OpenWebUIClient) -> bool:
    """Demonstrate multiple messages in the same chat."""
    logger.info("\n🔄 Multi-Message Chat Example")
    logger.info("=" * 40)
    
    chat_title = "Python Programming Help"
    
    # First message
    logger.info("📝 Sending first message...")
    result1 = client.chat(
        question="What is a Python list?",
        chat_title=chat_title,
        folder_name="Programming"
    )
    
    if result1 and result1.get("response"):
        print(f"\n🤖 First Response: {result1['response'][:150]}...")
        
        # Wait a moment, then send a follow-up
        time.sleep(1)
        
        # Second message in the same chat
        logger.info("📝 Sending follow-up message...")
        result2 = client.chat(
            question="Can you give me an example of creating and using a Python list?",
            chat_title=chat_title  # Same title will continue the conversation
        )
        
        if result2 and result2.get("response"):
            print(f"\n🤖 Follow-up Response: {result2['response'][:150]}...")
            logger.info("✅ Successfully continued conversation")
            return True
        else:
            logger.error("❌ Failed to send follow-up message")
            return False
    else:
        logger.error("❌ Failed to send first message")
        return False


def different_models_example(client: OpenWebUIClient) -> bool:
    """Demonstrate using different models."""
    logger.info("\n🤖 Different Models Example")
    logger.info("=" * 35)
    
    # Get available models first
    models = client.list_models()
    if not models or len(models) < 2:
        logger.warning("⚠️ Need at least 2 models for this example - skipping")
        return True  # This is acceptable, not a failure
    
    # Get the first two available models
    model1 = models[0].get('id', DEFAULT_MODEL)
    model2 = models[1].get('id', DEFAULT_MODEL) if len(models) > 1 else DEFAULT_MODEL
    
    logger.info(f"🎯 Using models: {model1} and {model2}")
    
    question = "What's the most interesting thing about space exploration?"
    
    # Chat with first model
    result1 = client.chat(
        question=question,
        chat_title=f"Space Chat - {model1}",
        model_id=model1,
        folder_name="Science"
    )
    
    if result1 and result1.get("response"):
        print(f"\n🤖 {model1}: {result1['response'][:150]}...")
    else:
        logger.error(f"❌ Failed to get response from {model1}")
        return False
    
    # Chat with second model  
    result2 = client.chat(
        question=question,
        chat_title=f"Space Chat - {model2}",
        model_id=model2,
        folder_name="Science"
    )
    
    if result2 and result2.get("response"):
        print(f"\n🤖 {model2}: {result2['response'][:150]}...")
        logger.info("✅ Successfully used different models")
        return True
    else:
        logger.error("❌ Failed to use different models")
        return False


def chat_management_example(client: OpenWebUIClient) -> bool:
    """Demonstrate basic chat management."""
    logger.info("\n🛠️ Chat Management Example")
    logger.info("=" * 35)
    
    # Create a chat to manage
    result = client.chat(
        question="What is artificial intelligence?",
        chat_title="AI Discussion - Original Title"
    )
    
    if result and result.get("chat_id"):
        chat_id = result["chat_id"]
        logger.info(f"✅ Created chat: {chat_id[:8]}...")
        
        # Rename the chat
        new_title = "AI Discussion - Updated Title"
        success = client.rename_chat(chat_id, new_title)
        
        if success:
            logger.info(f"✅ Successfully renamed chat to: {new_title}")
            return True
        else:
            logger.warning("⚠️ Failed to rename chat")
            return False
    else:
        logger.error("❌ Failed to create chat for management example")
        return False


def main() -> None:
    """Main function demonstrating basic chat functionality."""
    logger.info("🚀 OpenWebUI Chat Client - Basic Chat Examples")
    logger.info("=" * 60)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        # Test basic connectivity
        models = client.list_models()
        if not models:
            logger.error("❌ Failed to list models - connectivity or authentication issue")
            sys.exit(1)
        logger.info(f"Successfully listed {len(models)} models.")
        logger.info("✅ Client initialized successfully")
        
        # 🧹 Optional: Clean up all existing chats before running tests
        # Enable by setting OUI_CLEANUP_BEFORE_TEST=true
        if CLEANUP_BEFORE_TEST:
            logger.info("🧹 Cleaning up existing chats for clean test environment...")
            cleanup_success = client.delete_all_chats()
            if cleanup_success:
                logger.info("✅ Test environment cleaned (all previous chats deleted)")
            else:
                logger.warning("⚠️ Could not clean up previous chats, continuing anyway...")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Run examples and track success
    examples = [
        ("basic_chat", basic_chat_example),
        # ("organized_chat", organized_chat_example),
        # ("multi_message_chat", multi_message_chat_example),
        # ("different_models", different_models_example),
        # ("chat_management", chat_management_example)
    ]
    
    success_count = 0
    try:
        for example_name, example_func in examples:
            try:
                if example_func(client):
                    success_count += 1
                    logger.info(f"✅ {example_name} example completed successfully")
                else:
                    logger.error(f"❌ {example_name} example failed")
            except Exception as e:
                logger.error(f"❌ {example_name} example failed with exception: {e}")
        
        # Require most examples to succeed
        total_examples = len(examples)
        if success_count == 0:
            logger.error("❌ All basic chat examples failed")
            logger.error("This indicates a serious connectivity or functionality issue")
            sys.exit(1)
        # Require a majority when multiple examples are enabled; otherwise all must pass
        required_success = min(3, total_examples)
        if success_count < required_success:
            logger.error(f"❌ Only {success_count}/{total_examples} examples succeeded")
            logger.error("Integration test requires most basic features to work properly")
            sys.exit(1)
        
        logger.info(f"\n🎉 Basic chat examples completed successfully: {success_count}/{total_examples}!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/chat_features/streaming_chat.py")
        logger.info("   - Try: python examples/rag_knowledge/file_rag.py")
        logger.info("   - Try: python examples/chat_features/parallel_chat.py")
        
    except Exception as e:
        logger.error(f"❌ Basic chat examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()