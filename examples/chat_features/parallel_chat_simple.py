#!/usr/bin/env python3
"""
Simple Parallel Chat Example.

This example demonstrates basic parallel chat functionality with multiple models.

Features demonstrated:
- Sending questions to multiple models simultaneously
- Using chat_id to continue conversations
- Accessing responses from different models

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_PARALLEL_MODELS (comma-separated model IDs)

Usage:
    python examples/chat_features/parallel_chat_simple.py
"""

import logging
import os
import sys

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


def main():
    """Run parallel chat example."""
    logger.info("🚀 Simple Parallel Chat Example")
    logger.info("=" * 60)

    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        return 1

    if len(PARALLEL_MODELS) < 2:
        logger.error(f"❌ Need at least 2 models in OUI_PARALLEL_MODELS")
        logger.error(f"   Current: {PARALLEL_MODELS}")
        return 1

    # Initialize client
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
    logger.info(f"✅ Connected to: {BASE_URL}")
    logger.info(f"🤖 Using models: {PARALLEL_MODELS}")

    # Example 1: Simple parallel chat
    logger.info("\n" + "=" * 60)
    logger.info("Example 1: Basic Parallel Chat")
    logger.info("=" * 60)

    result1 = client.parallel_chat(
        question="What is the capital of France?",
        chat_title="Parallel Demo",
        model_ids=PARALLEL_MODELS[:2],
    )

    if result1 and result1.responses:
        logger.info(f"\n✅ Received {len(result1.responses)} responses:")
        for model_id, response_data in result1.responses.items():
            content = (
                response_data.content
                if hasattr(response_data, "content")
                else str(response_data)
            )
            print(f"\n🤖 {model_id}:")
            print(f"   {content[:150] if content else 'No content'}...")

        chat_id = result1.chat_id
        logger.info(f"\n💾 Chat ID: {chat_id}")
    else:
        logger.error("❌ Failed to get responses")
        return 1

    # Example 2: Continue conversation using chat_id
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Continue with chat_id")
    logger.info("=" * 60)

    result2 = client.parallel_chat(
        question="What about Germany?",
        chat_title="Parallel Demo",
        model_ids=PARALLEL_MODELS[:2],
        chat_id=chat_id,  # Continue in same chat
    )

    if result2 and result2.responses:
        logger.info(f"\n✅ Received {len(result2.responses)} responses:")
        for model_id, response_data in result2.responses.items():
            content = (
                response_data.content
                if hasattr(response_data, "content")
                else str(response_data)
            )
            print(f"\n🤖 {model_id}:")
            print(f"   {content[:150] if content else 'No content'}...")
    else:
        logger.error("❌ Failed to get responses")
        return 1

    # Example 3: Mix single and parallel chat
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Mix Single and Parallel")
    logger.info("=" * 60)

    # Single model question
    result3 = client.chat(
        question="Tell me more about European capitals.", chat_id=chat_id
    )

    if result3:
        logger.info(f"\n✅ Single model response:")
        print(f"   {result3.get_text()[:150]}...")

    # Then parallel comparison
    result4 = client.parallel_chat(
        question="Compare Paris and Berlin as capital cities.",
        chat_title="Parallel Demo",
        model_ids=PARALLEL_MODELS[:2],
        chat_id=chat_id,
    )

    if result4 and result4.responses:
        logger.info(f"\n✅ Parallel comparison ({len(result4.responses)} models):")
        for model_id, response_data in result4.responses.items():
            content = (
                response_data.content
                if hasattr(response_data, "content")
                else str(response_data)
            )
            print(f"\n🤖 {model_id}:")
            print(f"   {content[:150] if content else 'No content'}...")

    logger.info("\n" + "=" * 60)
    logger.info("🎉 All examples completed successfully!")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
