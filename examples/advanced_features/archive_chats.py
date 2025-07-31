#!/usr/bin/env python3
"""
Archive Chat Sessions Example

This example demonstrates how to use the archive functionality to:
- Archive individual chats
- Archive chats by age (time since last update)
- Filter by folder for selective archiving

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/advanced_features/archive_chats.py
"""

import logging
import os
from typing import Optional, Dict, Any

from openwebui_chat_client import OpenWebUIClient

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, environment variables should be set manually
    pass

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


def demonstrate_archive_individual_chat(client: OpenWebUIClient) -> None:
    """Demonstrate archiving an individual chat."""
    logger.info("=" * 60)
    logger.info("Demonstrating Individual Chat Archiving")
    logger.info("=" * 60)
    
    # List some chats first
    chats = client.list_chats(page=1)
    if not chats:
        logger.warning("No chats found to archive")
        return
    
    # Take the first chat as an example
    chat_to_archive = chats[0]
    chat_id = chat_to_archive["id"]
    chat_title = chat_to_archive.get("title", "Unknown")
    
    logger.info(f"Archiving chat: '{chat_title}' (ID: {chat_id[:8]}...)")
    
    success = client.archive_chat(chat_id)
    if success:
        logger.info("✅ Chat archived successfully!")
    else:
        logger.error("❌ Failed to archive chat")


def demonstrate_bulk_archive_no_folder(client: OpenWebUIClient) -> None:
    """Demonstrate bulk archiving of chats NOT in folders."""
    logger.info("=" * 60)
    logger.info("Demonstrating Bulk Archive (Chats NOT in Folders)")
    logger.info("=" * 60)
    
    # Archive chats older than 30 days that are NOT in folders
    results = client.archive_chats_by_age(days_since_update=30)
    
    logger.info(f"Archive Results:")
    logger.info(f"  Total checked: {results['total_checked']}")
    logger.info(f"  Total archived: {results['total_archived']}")
    logger.info(f"  Total failed: {results['total_failed']}")
    
    if results['archived_chats']:
        logger.info("  Archived chats:")
        for chat in results['archived_chats']:
            logger.info(f"    - {chat['title']} (ID: {chat['id'][:8]}...)")
    
    if results['failed_chats']:
        logger.warning("  Failed to archive:")
        for chat in results['failed_chats']:
            logger.warning(f"    - {chat['title']}: {chat['error']}")
    
    if results['errors']:
        logger.error("  Errors encountered:")
        for error in results['errors']:
            logger.error(f"    - {error}")


def demonstrate_bulk_archive_with_folder(client: OpenWebUIClient) -> None:
    """Demonstrate bulk archiving of chats in a specific folder."""
    logger.info("=" * 60)
    logger.info("Demonstrating Bulk Archive (Chats in Specific Folder)")
    logger.info("=" * 60)
    
    # You can specify a folder name to archive only chats in that folder
    folder_name = "OldProjects"  # Change this to an existing folder name
    
    # Archive chats older than 7 days in the specified folder
    results = client.archive_chats_by_age(
        days_since_update=7, 
        folder_name=folder_name
    )
    
    logger.info(f"Archive Results for folder '{folder_name}':")
    logger.info(f"  Total checked: {results['total_checked']}")
    logger.info(f"  Total archived: {results['total_archived']}")
    logger.info(f"  Total failed: {results['total_failed']}")
    
    if results['archived_chats']:
        logger.info("  Archived chats:")
        for chat in results['archived_chats']:
            logger.info(f"    - {chat['title']} (ID: {chat['id'][:8]}...)")
    
    if results['errors']:
        logger.error("  Errors encountered:")
        for error in results['errors']:
            logger.error(f"    - {error}")


def demonstrate_list_chats(client: OpenWebUIClient) -> None:
    """Demonstrate listing chats."""
    logger.info("=" * 60)
    logger.info("Demonstrating Chat Listing")
    logger.info("=" * 60)
    
    # List first page of chats
    chats = client.list_chats(page=1)
    if chats:
        logger.info(f"Found {len(chats)} chats on first page:")
        for chat in chats[:5]:  # Show first 5
            logger.info(f"  - {chat.get('title', 'No title')} (ID: {chat['id'][:8]}...)")
        if len(chats) > 5:
            logger.info(f"  ... and {len(chats) - 5} more chats")
    else:
        logger.warning("No chats found or failed to fetch chat list")


def demonstrate_folder_chats(client: OpenWebUIClient) -> None:
    """Demonstrate getting chats by folder."""
    logger.info("=" * 60)
    logger.info("Demonstrating Folder Chat Listing")
    logger.info("=" * 60)
    
    # First, let's see what folders exist
    try:
        response = client.session.get(
            f"{client.base_url}/api/v1/folders/",
            headers=client.json_headers
        )
        response.raise_for_status()
        folders = response.json()
        
        if folders:
            logger.info(f"Found {len(folders)} folders:")
            for folder in folders[:3]:  # Show first 3 folders
                folder_name = folder.get("name", "Unnamed")
                folder_id = folder.get("id")
                logger.info(f"  - {folder_name} (ID: {folder_id[:8] if folder_id else 'N/A'}...)")
                
                # Get chats in this folder
                folder_chats = client.get_chats_by_folder(folder_id)
                if folder_chats:
                    logger.info(f"    Contains {len(folder_chats)} chats")
                    for chat in folder_chats[:2]:  # Show first 2 chats
                        logger.info(f"      - {chat.get('title', 'No title')}")
                else:
                    logger.info("    No chats found in this folder")
        else:
            logger.info("No folders found")
            
    except Exception as e:
        logger.error(f"Failed to fetch folders: {e}")


def main() -> None:
    """Main function demonstrating archive functionality."""
    # Validate environment variables
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.info("Please set the following environment variables:")
        logger.info("  export OUI_BASE_URL='http://localhost:3000'")
        logger.info("  export OUI_AUTH_TOKEN='your_api_token_here'")
        return
    
    # Initialize client
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        return
    
    try:
        # Demonstrate different archive functionalities
        demonstrate_list_chats(client)
        demonstrate_folder_chats(client)
        
        # Note: Be careful with these operations as they will actually archive chats
        # Uncomment the following lines to test actual archiving:
        
        # demonstrate_archive_individual_chat(client)
        # demonstrate_bulk_archive_no_folder(client)
        # demonstrate_bulk_archive_with_folder(client)
        
        logger.info("🎉 Archive functionality demonstration completed")
        logger.info("Uncomment the archive functions in main() to test actual archiving")
        
    except Exception as e:
        logger.error(f"❌ Error during demonstration: {e}")


if __name__ == "__main__":
    main()