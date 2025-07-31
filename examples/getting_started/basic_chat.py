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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def basic_chat_example(client: OpenWebUIClient) -> None:
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
    else:
        logger.error("❌ Failed to get response")


def organized_chat_example(client: OpenWebUIClient) -> None:
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
    else:
        logger.error("❌ Failed to create organized chat")


def multi_message_chat_example(client: OpenWebUIClient) -> None:
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
        else:
            logger.error("❌ Failed to send follow-up message")
    else:
        logger.error("❌ Failed to send first message")


def different_models_example(client: OpenWebUIClient) -> None:
    """Demonstrate using different models."""
    logger.info("\n🤖 Different Models Example")
    logger.info("=" * 35)
    
    # Get available models first
    models = client.list_models()
    if not models or len(models) < 2:
        logger.warning("⚠️ Need at least 2 models for this example - skipping")
        return
    
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
    else:
        logger.error("❌ Failed to use different models")


def chat_management_example(client: OpenWebUIClient) -> None:
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
        else:
            logger.warning("⚠️ Failed to rename chat")
    else:
        logger.error("❌ Failed to create chat for management example")


def main() -> None:
    """Main function demonstrating basic chat functionality."""
    logger.info("🚀 OpenWebUI Chat Client - Basic Chat Examples")
    logger.info("=" * 60)
    
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
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        return
    
    # Run examples
    try:
        basic_chat_example(client)
        organized_chat_example(client)
        multi_message_chat_example(client)
        different_models_example(client)
        chat_management_example(client)
        
        logger.info("\n🎉 Basic chat examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/chat_features/streaming_chat.py")
        logger.info("   - Try: python examples/rag_knowledge/file_rag.py")
        logger.info("   - Try: python examples/chat_features/parallel_chat.py")
        
    except Exception as e:
        logger.error(f"❌ Basic chat examples failed: {e}")


if __name__ == "__main__":
    main()