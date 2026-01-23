#!/usr/bin/env python3
"""
Basic notes operations example for OpenWebUI Chat Client.

This example demonstrates fundamental Notes API operations including creating,
reading, updating, and deleting notes.

Features demonstrated:
- Creating notes with metadata
- Retrieving all notes and notes list
- Getting specific notes by ID
- Updating note content and metadata
- Deleting notes
- Error handling for notes operations

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/notes_api/basic_notes.py
"""

import logging
import os
import sys
from typing import Optional

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_note_example(client: OpenWebUIClient) -> Optional[str]:
    """Demonstrate creating a new note."""
    logger.info("📝 Creating a New Note")
    logger.info("=" * 30)

    try:
        new_note = client.create_note(
            title="OpenWebUI Chat Client Example Note",
            data={
                "content": "This is an example note created using the OpenWebUI Chat Client API.\n\nThis note demonstrates the notes functionality and how to create structured content.",
                "type": "markdown",
                "category": "example",
            },
            meta={
                "tags": ["example", "demo", "api-created"],
                "priority": "normal",
                "created_by": "openwebui-chat-client",
            },
        )

        if new_note:
            note_id = new_note["id"]
            logger.info("✅ Note created successfully!")
            logger.info(f"   Note ID: {note_id[:8]}...")
            logger.info(f"   Title: {new_note['title']}")
            logger.info(f"   Tags: {new_note.get('meta', {}).get('tags', [])}")
            return note_id
        else:
            logger.error("❌ Failed to create note")
            return None

    except Exception as e:
        logger.error(f"❌ Note creation failed: {e}")
        return None


def list_notes_example(client: OpenWebUIClient) -> None:
    """Demonstrate listing all notes."""
    logger.info("\n📋 Listing All Notes")
    logger.info("=" * 25)

    try:
        # Get all notes
        all_notes = client.get_notes()
        if all_notes:
            logger.info(f"✅ Retrieved {len(all_notes)} notes:")
            for i, note in enumerate(all_notes[:5], 1):  # Show first 5
                title = note.get("title", "Untitled")
                note_id = note.get("id", "Unknown")
                created_at = note.get("created_at", "Unknown")
                logger.info(f"   {i}. {title}")
                logger.info(f"      ID: {note_id[:8]}... | Created: {created_at}")

            if len(all_notes) > 5:
                logger.info(f"   ... and {len(all_notes) - 5} more notes")
        else:
            logger.warning("⚠️ No notes found")

    except Exception as e:
        logger.error(f"❌ Failed to list notes: {e}")


def list_notes_simple_example(client: OpenWebUIClient) -> None:
    """Demonstrate getting simplified notes list."""
    logger.info("\n📄 Getting Notes List (Simplified)")
    logger.info("=" * 45)

    try:
        # Get notes list (simplified format)
        notes_list = client.get_notes_list()
        if notes_list:
            logger.info(f"✅ Retrieved simplified list with {len(notes_list)} items:")
            for i, note in enumerate(notes_list[:3], 1):  # Show first 3
                title = note.get("title", "Untitled")
                note_id = note.get("id", "Unknown")
                logger.info(f"   {i}. {title} ({note_id[:8]}...)")
        else:
            logger.warning("⚠️ No notes found in simplified list")

    except Exception as e:
        logger.error(f"❌ Failed to get notes list: {e}")


def get_note_by_id_example(client: OpenWebUIClient, note_id: str) -> None:
    """Demonstrate retrieving a specific note by ID."""
    logger.info(f"\n🔍 Getting Note by ID: {note_id[:8]}...")
    logger.info("=" * 50)

    try:
        retrieved_note = client.get_note_by_id(note_id)
        if retrieved_note:
            logger.info("✅ Note retrieved successfully:")
            logger.info(f"   Title: {retrieved_note.get('title', 'Untitled')}")
            logger.info(
                f"   Content: {retrieved_note.get('data', {}).get('content', 'No content')[:100]}..."
            )
            logger.info(
                f"   Type: {retrieved_note.get('data', {}).get('type', 'Unknown')}"
            )
            logger.info(f"   Tags: {retrieved_note.get('meta', {}).get('tags', [])}")
        else:
            logger.warning(f"⚠️ Note with ID {note_id[:8]}... not found")

    except Exception as e:
        logger.error(f"❌ Failed to get note by ID: {e}")


def update_note_example(client: OpenWebUIClient, note_id: str) -> None:
    """Demonstrate updating an existing note."""
    logger.info(f"\n✏️ Updating Note: {note_id[:8]}...")
    logger.info("=" * 40)

    try:
        updated_note = client.update_note_by_id(
            note_id=note_id,
            title="OpenWebUI Chat Client Example Note (Updated)",
            data={
                "content": "This note has been UPDATED using the OpenWebUI Chat Client API.\n\nThis demonstrates how to modify existing notes programmatically.\n\n### New Section\nThis section was added during the update.",
                "type": "markdown",
                "category": "example",
                "last_modified": "via API update",
            },
            meta={
                "tags": ["example", "demo", "api-created", "updated"],
                "priority": "high",
                "created_by": "openwebui-chat-client",
                "updated_by": "api-update-example",
            },
        )

        if updated_note:
            logger.info("✅ Note updated successfully!")
            logger.info(f"   New Title: {updated_note.get('title', 'Unknown')}")
            logger.info(
                f"   Updated Content Length: {len(updated_note.get('data', {}).get('content', ''))} characters"
            )
            logger.info(f"   New Tags: {updated_note.get('meta', {}).get('tags', [])}")
        else:
            logger.error("❌ Failed to update note")

    except Exception as e:
        logger.error(f"❌ Note update failed: {e}")


def delete_note_example(client: OpenWebUIClient, note_id: str) -> None:
    """Demonstrate deleting a note."""
    logger.info(f"\n🗑️ Deleting Note: {note_id[:8]}...")
    logger.info("=" * 40)

    try:
        deleted = client.delete_note_by_id(note_id)
        if deleted:
            logger.info("✅ Note deleted successfully!")

            # Verify deletion
            verification = client.get_note_by_id(note_id)
            if not verification:
                logger.info("✅ Note deletion verified")
            else:
                logger.warning("⚠️ Note still exists after deletion attempt")
        else:
            logger.error("❌ Failed to delete note")

    except Exception as e:
        logger.error(f"❌ Note deletion failed: {e}")


def notes_error_handling_example(client: OpenWebUIClient) -> None:
    """Demonstrate error handling for notes operations."""
    logger.info("\n⚠️ Notes Error Handling Example")
    logger.info("=" * 45)

    # Test with non-existent note ID
    fake_note_id = "non-existent-note-id-12345"
    logger.info(f"🧪 Testing with non-existent note ID: {fake_note_id}")

    try:
        note = client.get_note_by_id(fake_note_id)
        if note:
            logger.warning("⚠️ Unexpectedly found note with fake ID")
        else:
            logger.info("✅ Correctly handled non-existent note ID")
    except Exception as e:
        logger.info(f"✅ Error handled correctly: {e}")

    # Test updating non-existent note
    logger.info("🧪 Testing update of non-existent note...")

    try:
        result = client.update_note_by_id(
            note_id=fake_note_id,
            title="This should fail",
            data={"content": "This should not work"},
            meta={"tags": ["test"]},
        )

        if result:
            logger.warning("⚠️ Unexpectedly succeeded in updating non-existent note")
        else:
            logger.info("✅ Correctly failed to update non-existent note")
    except Exception as e:
        logger.info(f"✅ Update error handled correctly: {e}")

    # Test deleting non-existent note
    logger.info("🧪 Testing deletion of non-existent note...")

    try:
        result = client.delete_note_by_id(fake_note_id)
        if result:
            logger.warning("⚠️ Unexpectedly succeeded in deleting non-existent note")
        else:
            logger.info("✅ Correctly failed to delete non-existent note")
    except Exception as e:
        logger.info(f"✅ Delete error handled correctly: {e}")


def main() -> None:
    """Main function demonstrating basic notes operations."""
    logger.info("🚀 OpenWebUI Chat Client - Basic Notes API Examples")
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
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)

    # Run notes examples
    try:
        # Create a note for testing
        note_id = create_note_example(client)

        if note_id:
            # List notes
            list_notes_example(client)
            list_notes_simple_example(client)

            # Get specific note
            get_note_by_id_example(client, note_id)

            # Update the note
            update_note_example(client, note_id)

            # Verify the update
            get_note_by_id_example(client, note_id)

            # Clean up by deleting the note
            delete_note_example(client, note_id)

        # Test error handling
        notes_error_handling_example(client)

        logger.info("\n🎉 Basic notes examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/notes_api/advanced_notes.py")
        logger.info("   - Try: python examples/getting_started/basic_chat.py")

    except Exception as e:
        logger.error(f"❌ Basic notes examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
