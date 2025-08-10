#!/usr/bin/env python3
"""
Basic Prompts API Example for OpenWebUI Chat Client.

This example demonstrates basic CRUD operations for prompts:
- Creating prompts with variables
- Retrieving prompts  
- Updating prompts
- Deleting prompts
- Variable substitution

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/prompts_api/basic_prompts.py
"""

import logging
import os
from typing import Optional, Dict, Any, List

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


def demonstrate_basic_prompts_operations(client: OpenWebUIClient, timestamp: str):
    """Demonstrate basic prompts CRUD operations."""
    logger.info("=== Basic Prompts Operations Demo ===")
    
    # Use unique commands with timestamp to avoid conflicts
    summarize_command = f"/test_summarize_{timestamp}"
    email_command = f"/test_email_{timestamp}"
    
    # Check if prompts already exist and clean them up first
    logger.info("Checking for existing test prompts...")
    existing_summarize = client.get_prompt_by_command(summarize_command)
    if existing_summarize:
        logger.info(f"Found existing prompt '{summarize_command}', deleting it first...")
        client.delete_prompt_by_command(summarize_command)
    
    existing_email = client.get_prompt_by_command(email_command)
    if existing_email:
        logger.info(f"Found existing prompt '{email_command}', deleting it first...")
        client.delete_prompt_by_command(email_command)
    
    # 1. Create a simple prompt
    logger.info("Creating a simple summarization prompt...")
    summary_prompt = client.create_prompt(
        command=summarize_command,
        title="Text Summarizer Test", 
        content="Please provide a concise summary of the following text:\n\n{{text}}"
    )
    
    if summary_prompt:
        logger.info(f"✅ Created prompt: {summary_prompt['command']} - {summary_prompt['title']}")
    else:
        logger.error("❌ Failed to create summarization prompt")
        return
    
    # 2. Create a more complex prompt with multiple variables
    logger.info("Creating a complex email prompt with multiple variables...")
    email_prompt = client.create_prompt(
        command=email_command,
        title="Professional Email Generator Test",
        content="""Write a professional email with the following details:

To: {{recipient}}
Subject: {{subject}}
Tone: {{tone}}

Email body:
{{message}}

Please format this as a complete professional email."""
    )
    
    if email_prompt:
        logger.info(f"✅ Created prompt: {email_prompt['command']} - {email_prompt['title']}")
    
    # 3. List all prompts
    logger.info("Retrieving all prompts...")
    all_prompts = client.get_prompts()
    if all_prompts:
        logger.info(f"📋 Found {len(all_prompts)} prompts:")
        # Only show our test prompts to avoid cluttering logs
        test_prompts = [p for p in all_prompts if timestamp in p['command']]
        for prompt in test_prompts:
            logger.info(f"  - {prompt['command']}: {prompt['title']}")
    
    # 4. Get a specific prompt by command
    logger.info("Retrieving specific prompt by command...")
    retrieved_prompt = client.get_prompt_by_command(summarize_command)
    if retrieved_prompt:
        logger.info(f"📄 Retrieved prompt: {retrieved_prompt['title']}")
        logger.info(f"   Content preview: {retrieved_prompt['content'][:50]}...")
    
    # 5. Update a prompt
    logger.info("Updating the summarization prompt...")
    updated_prompt = client.update_prompt_by_command(
        command=summarize_command,
        content="Please provide a detailed summary with key points of the following text:\n\n{{text}}\n\nKey Points:\n-"
    )
    
    if updated_prompt:
        logger.info("✅ Successfully updated prompt")
    
    return [summarize_command, email_command]


def demonstrate_variable_operations(client: OpenWebUIClient):
    """Demonstrate variable extraction and substitution."""
    logger.info("\n=== Variable Operations Demo ===")
    
    # Create a prompt with various variable types
    template_content = """Generate a {{document_type}} for {{client_name}}.

Details:
- Priority: {{priority | select:options=["High","Medium","Low"]}}
- Due Date: {{due_date | date}}
- Requirements: {{requirements | textarea}}
- Budget: ${{budget | number}}
- Include summary: {{include_summary | checkbox}}

Additional notes: {{notes}}"""
    
    # Extract variables
    logger.info("Extracting variables from prompt content...")
    variables = client.extract_variables(template_content)
    logger.info(f"📝 Found variables: {variables}")
    
    # Create sample data for substitution
    sample_data = {
        "document_type": "project proposal",
        "client_name": "ABC Corporation",
        "priority": "High",
        "due_date": "2024-02-15",
        "requirements": "Design and development of web application",
        "budget": 50000,
        "include_summary": "Yes",
        "notes": "Client prefers modern tech stack"
    }
    
    # Get system variables
    system_vars = client.get_system_variables()
    logger.info(f"🔧 System variables available: {list(system_vars.keys())}")
    
    # Add system variables to template
    enhanced_template = f"Generated on {{{{CURRENT_DATE}}}} at {{{{CURRENT_TIME}}}}\n\n{template_content}"
    
    # Substitute variables
    logger.info("Substituting variables in template...")
    final_content = client.substitute_variables(enhanced_template, sample_data, system_vars)
    
    logger.info("📋 Final content after substitution:")
    logger.info("-" * 50)
    logger.info(final_content)
    logger.info("-" * 50)


def demonstrate_search_operations(client: OpenWebUIClient, timestamp: str):
    """Demonstrate prompt search functionality."""
    logger.info("\n=== Search Operations Demo ===")
    
    # Create some test prompts for searching with unique commands
    test_prompts = [
        {
            "command": f"/test_translate_{timestamp}",
            "title": "Language Translator Test",
            "content": "Translate the following {{source_language}} text to {{target_language}}:\n\n{{text}}"
        },
        {
            "command": f"/test_review_{timestamp}",
            "title": "Code Reviewer Test", 
            "content": "Review the following {{language}} code and provide feedback:\n\n{{code}}"
        },
        {
            "command": f"/test_brainstorm_{timestamp}",
            "title": "Idea Generator Test",
            "content": "Generate creative ideas for {{topic}} considering {{constraints}}"
        }
    ]
    
    created_commands = []
    
    # Create test prompts
    logger.info("Creating test prompts for search demo...")
    for prompt_data in test_prompts:
        # Check if prompt already exists and delete it
        existing = client.get_prompt_by_command(prompt_data["command"])
        if existing:
            logger.info(f"Found existing prompt '{prompt_data['command']}', deleting it first...")
            client.delete_prompt_by_command(prompt_data["command"])
            
        result = client.create_prompt(**prompt_data)
        if result:
            created_commands.append(prompt_data["command"])
    
    # Search by title
    logger.info("Searching prompts by title containing 'test'...")
    title_results = client.search_prompts("test", by_title=True)
    # Filter to only our test prompts
    our_title_results = [p for p in title_results if timestamp in p['command']]
    logger.info(f"🔍 Found {len(our_title_results)} test prompts by title")
    
    # Search by command
    logger.info("Searching prompts by command containing 'translate'...")
    command_results = client.search_prompts("translate", by_command=True)
    # Filter to only our test prompts
    our_command_results = [p for p in command_results if timestamp in p['command']]
    logger.info(f"🔍 Found {len(our_command_results)} test prompts by command")
    
    # Search by content
    logger.info("Searching prompts by content containing 'code'...")
    content_results = client.search_prompts("code", by_content=True)
    # Filter to only our test prompts
    our_content_results = [p for p in content_results if timestamp in p['command']]
    logger.info(f"🔍 Found {len(our_content_results)} test prompts by content")
    
    return created_commands


def demonstrate_batch_operations(client: OpenWebUIClient, timestamp: str):
    """Demonstrate batch operations for prompts."""
    logger.info("\n=== Batch Operations Demo ===")
    
    # Prepare batch data with unique commands
    batch_prompts = [
        {
            "command": f"/test_meeting_notes_{timestamp}",
            "title": "Meeting Notes Generator Test",
            "content": "Generate meeting notes for {{meeting_type}} on {{date}} with {{attendees}}"
        },
        {
            "command": f"/test_social_post_{timestamp}",
            "title": "Social Media Post Creator Test",
            "content": "Create a {{platform}} post about {{topic}} with {{tone}} tone"
        },
        {
            "command": f"/test_bug_report_{timestamp}",
            "title": "Bug Report Template Test",
            "content": "Bug Report:\nTitle: {{title}}\nSteps: {{steps}}\nExpected: {{expected}}\nActual: {{actual}}"
        }
    ]
    
    # Check for existing prompts and clean them up first
    for prompt_data in batch_prompts:
        existing = client.get_prompt_by_command(prompt_data["command"])
        if existing:
            logger.info(f"Found existing prompt '{prompt_data['command']}', deleting it first...")
            client.delete_prompt_by_command(prompt_data["command"])
    
    # Batch create
    logger.info(f"Creating {len(batch_prompts)} prompts in batch...")
    create_results = client.batch_create_prompts(batch_prompts)
    
    logger.info(f"✅ Batch creation results:")
    logger.info(f"   Success: {len(create_results['success'])}")
    logger.info(f"   Failed: {len(create_results['failed'])}")
    
    # Return commands for cleanup
    created_commands = [p['command'] for p in create_results['success']]
    
    # If we have successful creates, demonstrate batch delete
    if create_results['success']:
        commands_to_delete = [p['command'] for p in create_results['success']]
        logger.info(f"Deleting {len(commands_to_delete)} prompts in batch...")
        
        delete_results = client.batch_delete_prompts(commands_to_delete)
        logger.info(f"🗑️ Batch deletion results:")
        logger.info(f"   Success: {len(delete_results['success'])}")
        logger.info(f"   Failed: {len(delete_results['failed'])}")
        
        # Return empty list since we already deleted them
        created_commands = []
    
    return created_commands


def cleanup_demo_prompts(client: OpenWebUIClient, commands_to_cleanup: List[str]):
    """Clean up prompts created during the demo."""
    if not commands_to_cleanup:
        logger.info("No prompts to clean up")
        return
        
    logger.info("\n=== Cleanup Demo Prompts ===")
    
    logger.info(f"Cleaning up {len(commands_to_cleanup)} demo prompts...")
    cleanup_results = client.batch_delete_prompts(commands_to_cleanup, continue_on_error=True)
    
    logger.info(f"🧹 Cleanup results:")
    logger.info(f"   Deleted: {len(cleanup_results['success'])}")
    logger.info(f"   Not found/failed: {len(cleanup_results['failed'])}")


def main():
    """Main function demonstrating prompts functionality."""
    # Validate environment variables
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.info("Please set your OpenWebUI API token:")
        logger.info("export OUI_AUTH_TOKEN='your_api_token_here'")
        return
    
    # Initialize client
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        return
    
    # Generate timestamp for unique commands
    import time
    timestamp = str(int(time.time()))
    
    # Track all created prompts for cleanup
    all_created_commands = []
    
    try:
        # Run demonstrations
        basic_commands = demonstrate_basic_prompts_operations(client, timestamp)
        if basic_commands:
            all_created_commands.extend(basic_commands)
            
        demonstrate_variable_operations(client)
        
        search_commands = demonstrate_search_operations(client, timestamp)
        if search_commands:
            all_created_commands.extend(search_commands)
            
        batch_commands = demonstrate_batch_operations(client, timestamp)
        if batch_commands:
            all_created_commands.extend(batch_commands)
        
        logger.info("\n🎉 Prompts API demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        # Still try to clean up even if demo failed
        logger.info("Attempting cleanup despite failure...")
        if all_created_commands:
            cleanup_demo_prompts(client, all_created_commands)
        raise
    
    # Always cleanup in CI environment, ask in interactive mode
    ci_mode = os.getenv("CI", "").lower() in ("true", "1", "yes")
    github_actions = os.getenv("GITHUB_ACTIONS", "").lower() in ("true", "1", "yes")
    
    if ci_mode or github_actions:
        # Always cleanup in CI environment
        logger.info("Running in CI environment - automatically cleaning up test prompts")
        cleanup_demo_prompts(client, all_created_commands)
    else:
        # Ask user in interactive mode
        if all_created_commands:
            response = input(f"\nDo you want to clean up {len(all_created_commands)} demo prompts? (y/N): ")
            if response.lower() == 'y':
                cleanup_demo_prompts(client, all_created_commands)


if __name__ == "__main__":
    main()