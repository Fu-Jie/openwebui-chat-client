#!/usr/bin/env python3
"""
Test Chat Cleanup Script

This script cleans up all chat sessions before running integration tests.
It ensures a clean test environment by removing all existing chats.

Usage:
    python .github/scripts/cleanup_test_chats.py

Environment Variables:
    OUI_BASE_URL: OpenWebUI instance URL (required)
    OUI_AUTH_TOKEN: Authentication token (required)
    OUI_DEFAULT_MODEL: Default model ID (optional)
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

from openwebui_chat_client import OpenWebUIClient  # noqa: E402

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cleanup_all_chats() -> bool:
    """
    Clean up all chat sessions.

    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    logger.info("🧹 Starting chat cleanup process...")

    # Validate environment
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        return False

    try:
        # Initialize client
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info(f"✅ Connected to OpenWebUI at {BASE_URL}")

        # Get current chat count
        chats_before = client.list_chats(page=1)
        if chats_before is not None:
            logger.info(f"📊 Found {len(chats_before)} chat(s) to clean up")
        else:
            logger.warning("⚠️ Could not retrieve chat list")

        # Delete all chats
        success = client.delete_all_chats()

        if success:
            logger.info("✅ Successfully deleted all chats")

            # Verify cleanup
            chats_after = client.list_chats(page=1)
            if chats_after is not None:
                if len(chats_after) == 0:
                    logger.info("✅ Verified: No chats remaining")
                else:
                    logger.warning(
                        f"⚠️ {len(chats_after)} chat(s) still present after cleanup"
                    )

            return True
        else:
            logger.error("❌ Failed to delete all chats")
            return False

    except Exception as e:
        logger.error(f"❌ Cleanup failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> None:
    """Main function."""
    logger.info("=" * 60)
    logger.info("🧹 OpenWebUI Chat Cleanup Script")
    logger.info("=" * 60)

    success = cleanup_all_chats()

    logger.info("=" * 60)
    if success:
        logger.info("✅ Cleanup completed successfully")
        logger.info("🎯 Test environment is ready for integration tests")
        sys.exit(0)
    else:
        logger.error("❌ Cleanup failed")
        logger.error("⚠️ Integration tests may run with existing chat data")
        sys.exit(1)


if __name__ == "__main__":
    main()
