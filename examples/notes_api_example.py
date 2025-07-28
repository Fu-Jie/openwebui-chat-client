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

def main():
    # Initialize the client (replace with your actual values)
    client = OpenWebUIClient(
        base_url="https://your-openwebui-instance.com",
        token="your-access-token",
        default_model_id="your-default-model"
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
    # Note: This is just an example. You need to provide actual credentials
    # and an actual OpenWebUI instance URL for this to work.
    print("This is an example script demonstrating Notes API usage.")
    print("To run it with real data, update the client initialization with your actual credentials.")
    
    # Uncomment the line below and provide real credentials to test:
    # main()