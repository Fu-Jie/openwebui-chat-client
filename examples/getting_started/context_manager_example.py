#!/usr/bin/env python3
"""
Example demonstrating context manager usage with OpenWebUIClient.

This example shows:
- Using the client as a context manager for automatic resource cleanup
- Traditional usage with explicit close() call
- Best practices for resource management

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_DEFAULT_MODEL (optional)

Usage:
    python examples/getting_started/context_manager_example.py
"""

import logging
import os
from dotenv import load_dotenv
from openwebui_chat_client import OpenWebUIClient

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


def example_with_context_manager():
    """
    Demonstrate using the client as a context manager.
    
    This is the RECOMMENDED approach as it ensures resources are
    automatically cleaned up, even if an exception occurs.
    """
    logger.info("\n" + "="*60)
    logger.info("Example 1: Using Context Manager (Recommended)")
    logger.info("="*60)
    
    try:
        # Use 'with' statement for automatic resource management
        with OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
            logger.info("✅ Client created and entered context")
            
            # Perform chat operations
            result = client.chat(
                question="What is the capital of France?",
                chat_title="Context Manager Example"
            )
            
            if result:
                logger.info(f"📝 Response: {result['response']}")
                logger.info(f"💬 Chat ID: {result['chat_id']}")
            else:
                logger.error("❌ Chat failed")
        
        # Resources are automatically cleaned up here
        logger.info("✅ Context exited, resources cleaned up automatically")
        
    except Exception as e:
        logger.error(f"❌ Error occurred: {e}")
        # Note: Resources are still cleaned up even when exception occurs


def example_with_explicit_close():
    """
    Demonstrate using the client with explicit close() call.
    
    This approach requires manually calling close() to cleanup resources.
    Use try-finally to ensure cleanup happens even if an error occurs.
    """
    logger.info("\n" + "="*60)
    logger.info("Example 2: Using Explicit close() Call")
    logger.info("="*60)
    
    client = None
    try:
        # Create client
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client created")
        
        # Perform chat operations
        result = client.chat(
            question="What is 2 + 2?",
            chat_title="Explicit Close Example"
        )
        
        if result:
            logger.info(f"📝 Response: {result['response']}")
            logger.info(f"💬 Chat ID: {result['chat_id']}")
        else:
            logger.error("❌ Chat failed")
            
    except Exception as e:
        logger.error(f"❌ Error occurred: {e}")
        
    finally:
        # Always cleanup resources in finally block
        if client:
            client.close()
            logger.info("✅ Client closed explicitly")


def example_exception_handling():
    """
    Demonstrate that context manager cleans up resources even when exceptions occur.
    """
    logger.info("\n" + "="*60)
    logger.info("Example 3: Exception Handling with Context Manager")
    logger.info("="*60)
    
    try:
        with OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
            logger.info("✅ Client created")
            
            # Simulate some work
            result = client.chat(
                question="Test question",
                chat_title="Exception Test"
            )
            
            # Simulate an error
            raise ValueError("Simulated error for demonstration")
            
    except ValueError as e:
        logger.info(f"⚠️ Caught expected exception: {e}")
        logger.info("✅ Resources were still cleaned up properly")


def example_multiple_operations():
    """
    Demonstrate using context manager for multiple operations.
    """
    logger.info("\n" + "="*60)
    logger.info("Example 4: Multiple Operations in One Context")
    logger.info("="*60)
    
    with OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
        logger.info("✅ Client created")
        
        # Operation 1: First chat
        result1 = client.chat(
            question="What is Python?",
            chat_title="Multiple Operations Example"
        )
        if result1:
            logger.info(f"📝 First response: {result1['response'][:50]}...")
        
        # Operation 2: List models
        models = client.list_models()
        if models:
            logger.info(f"🤖 Available models: {len(models)} models found")
        
        # Operation 3: Second chat in same conversation
        result2 = client.chat(
            question="Give me a simple example.",
            chat_title="Multiple Operations Example"
        )
        if result2:
            logger.info(f"📝 Second response: {result2['response'][:50]}...")
    
    logger.info("✅ All operations completed, resources cleaned up")


def main():
    """Main function to run all examples."""
    # Validate environment
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable is not set")
        logger.error("Please set it to your OpenWebUI authentication token")
        return
    
    logger.info("🚀 OpenWebUI Client - Context Manager Examples")
    logger.info(f"📍 Base URL: {BASE_URL}")
    logger.info(f"🤖 Default Model: {DEFAULT_MODEL}")
    
    # Run examples
    example_with_context_manager()
    example_with_explicit_close()
    example_exception_handling()
    example_multiple_operations()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 All examples completed successfully!")
    logger.info("="*60)
    
    logger.info("\n💡 Best Practices:")
    logger.info("  1. Use context manager (with statement) whenever possible")
    logger.info("  2. It ensures automatic resource cleanup")
    logger.info("  3. Resources are cleaned up even if exceptions occur")
    logger.info("  4. If not using context manager, always call close() in finally block")


if __name__ == "__main__":
    main()
