#!/usr/bin/env python3
"""
Example usage of the Notes API functionality in openwebui-chat-client.

This example demonstrates how to use all the Notes API methods:
- get_notes()
- get_notes_list()
- create_note()
- get_note_by_id()
- update_note_by_id()
- delete_note_by_id()
"""

from openwebui_chat_client import OpenWebUIClient
import json
import os

def main():
    # Configuration from Environment Variables
    BASE_URL = os.getenv("OUI_BASE_URL", "https://your-openwebui-instance.com")
    AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN", "your-access-token")
    DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "your-default-model")
    
    # Initialize the client
    client = OpenWebUIClient(
        base_url=BASE_URL,
        token=AUTH_TOKEN,
        default_model_id=DEFAULT_MODEL
    )
    
    print("=== Notes API Example ===\n")
    
    # 1. Create a new note
    print("1. Creating a new note...")
    new_note = client.create_note(
        title="My Example Note",
        data={
            "content": "This is the content of my note",
            "type": "markdown"
        },
        meta={
            "tags": ["example", "demo"],
            "category": "tutorial"
        }
    )
    
    if new_note:
        note_id = new_note["id"]
        print(f"   ✅ Created note with ID: {note_id}")
        print(f"   Title: {new_note['title']}")
    else:
        print("   ❌ Failed to create note")
        return
    
    # 2. Get all notes
    print("\n2. Getting all notes...")
    all_notes = client.get_notes()
    if all_notes:
        print(f"   ✅ Retrieved {len(all_notes)} notes")
        for note in all_notes[:3]:  # Show first 3 notes
            print(f"   - {note['title']} (ID: {note['id'][:8]}...)")
    else:
        print("   ❌ Failed to get notes")
    
    # 3. Get notes list (simplified)
    print("\n3. Getting notes list...")
    notes_list = client.get_notes_list()
    if notes_list:
        print(f"   ✅ Retrieved notes list with {len(notes_list)} items")
        for note in notes_list[:3]:  # Show first 3 notes
            print(f"   - {note['title']} (ID: {note['id'][:8]}...)")
    else:
        print("   ❌ Failed to get notes list")
    
    # 4. Get specific note by ID
    print(f"\n4. Getting note by ID: {note_id}")
    retrieved_note = client.get_note_by_id(note_id)
    if retrieved_note:
        print(f"   ✅ Retrieved note: {retrieved_note['title']}")
        print(f"   Content: {retrieved_note.get('data', {}).get('content', 'No content')}")
    else:
        print("   ❌ Failed to get note by ID")
    
    # 5. Update the note
    print(f"\n5. Updating note: {note_id}")
    updated_note = client.update_note_by_id(
        note_id=note_id,
        title="My Updated Example Note",
        data={
            "content": "This is the UPDATED content of my note",
            "type": "markdown"
        },
        meta={
            "tags": ["example", "demo", "updated"],
            "category": "tutorial"
        }
    )
    
    if updated_note:
        print(f"   ✅ Updated note: {updated_note['title']}")
        print(f"   New content: {updated_note.get('data', {}).get('content', 'No content')}")
    else:
        print("   ❌ Failed to update note")
    
    # 6. Delete the note
    print(f"\n6. Deleting note: {note_id}")
    deleted = client.delete_note_by_id(note_id)
    if deleted:
        print("   ✅ Note deleted successfully")
    else:
        print("   ❌ Failed to delete note")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    # Configuration from Environment Variables
    # Set these environment variables to use the script:
    #
    # In Linux/macOS:
    #   export OUI_BASE_URL="https://your-openwebui-instance.com"
    #   export OUI_AUTH_TOKEN="your-access-token"
    #   export OUI_DEFAULT_MODEL="your-default-model"
    #
    # In Windows (Command Prompt):
    #   set OUI_BASE_URL="https://your-openwebui-instance.com"
    #   set OUI_AUTH_TOKEN="your-access-token"
    #   set OUI_DEFAULT_MODEL="your-default-model"
    #
    # In Windows (PowerShell):
    #   $env:OUI_BASE_URL="https://your-openwebui-instance.com"
    #   $env:OUI_AUTH_TOKEN="your-access-token"
    #   $env:OUI_DEFAULT_MODEL="your-default-model"
    #
    print("This is an example script demonstrating Notes API usage.")
    print("Set the environment variables OUI_BASE_URL, OUI_AUTH_TOKEN, and OUI_DEFAULT_MODEL to run with real data.")
    
    # Uncomment the line below and set environment variables to test:
    # main()