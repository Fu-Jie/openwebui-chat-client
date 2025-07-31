#!/usr/bin/env python3
"""
Hello World - Simplest possible OpenWebUI Chat Client example.

This is the most basic example showing how to initialize the client and send
a simple chat message. Perfect for getting started and testing your setup.

Features demonstrated:
- Basic client initialization
- Simple chat message
- Basic error handling

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/getting_started/hello_world.py
"""

import logging
import os
import sys
from typing import Optional

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


def main() -> None:
    """Main function demonstrating the simplest possible example."""
    logger.info("👋 Hello World - OpenWebUI Chat Client")
    logger.info("=" * 50)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        return
    
    # Client initialization
    try:
        logger.info("🔧 Initializing OpenWebUI client...")
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        return
    
    # Send a simple hello message
    try:
        logger.info("💬 Sending hello message...")
        
        result = client.chat(
            question="Hello! Please introduce yourself briefly.",
            chat_title="Hello World Chat"
        )
        
        if result and result.get("response"):
            logger.info("✅ Received response!")
            print("\n" + "=" * 50)
            print("🤖 AI Response:")
            print("=" * 50)
            print(result["response"])
            print("=" * 50)
            
            # Show chat information if available
            if result.get("chat_id"):
                logger.info(f"💾 Chat saved with ID: {result['chat_id'][:8]}...")
        else:
            logger.error("❌ No response received")
            
    except Exception as e:
        logger.error(f"❌ Chat failed: {e}")
        return
    
    logger.info("🎉 Hello World example completed successfully!")
    logger.info("💡 Next step: Try examples/getting_started/basic_chat.py")


if __name__ == "__main__":
    main()