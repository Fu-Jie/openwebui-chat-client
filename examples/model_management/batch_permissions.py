#!/usr/bin/env python3
"""
Batch Model Permissions Management Example

This example demonstrates how to batch update model permissions using the OpenWebUI Chat Client.
It shows how to set public, private, and group-based permissions for multiple models.

Features demonstrated:
- List available groups
- Update model permissions by model IDs
- Update model permissions by keyword filtering
- Set public, private, and group permissions
- Resolve group names to IDs

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Model availability: Various models for testing

Usage:
    python examples/model_management/batch_permissions.py
"""

import logging
import os
from typing import List, Dict, Any

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Log setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_list_groups(client: OpenWebUIClient) -> List[Dict[str, Any]]:
    """Demonstrate listing available groups."""
    logger.info("=" * 60)
    logger.info("🔍 Listing Available Groups")
    logger.info("=" * 60)
    
    groups = client.list_groups()
    if groups:
        logger.info(f"Found {len(groups)} groups:")
        for group in groups:
            logger.info(f"  - {group['name']} (ID: {group['id']})")
            logger.info(f"    Description: {group.get('description', 'No description')}")
            logger.info(f"    Users: {len(group.get('user_ids', []))}")
        return groups
    else:
        logger.warning("No groups found or failed to retrieve groups")
        return []


def demo_set_models_public(client: OpenWebUIClient, model_ids: List[str]) -> None:
    """Demonstrate setting models to public permissions."""
    logger.info("=" * 60)
    logger.info("🌐 Setting Models to Public Permissions")
    logger.info("=" * 60)
    
    result = client.batch_update_model_permissions(
        model_identifiers=model_ids,
        permission_type="public"
    )
    
    logger.info(f"✅ Successfully updated: {len(result['success'])} models")
    for model_id in result['success']:
        logger.info(f"  - {model_id}")
    
    if result['failed']:
        logger.warning(f"❌ Failed to update: {len(result['failed'])} models")
        for failure in result['failed']:
            logger.warning(f"  - {failure['model_id']}: {failure['error']}")


def demo_set_models_private(client: OpenWebUIClient, model_keyword: str, user_ids: List[str]) -> None:
    """Demonstrate setting models to private permissions with specific users."""
    logger.info("=" * 60)
    logger.info(f"🔒 Setting Models with keyword '{model_keyword}' to Private Permissions")
    logger.info("=" * 60)
    
    result = client.batch_update_model_permissions(
        model_keyword=model_keyword,
        permission_type="private",
        user_ids=user_ids
    )
    
    logger.info(f"✅ Successfully updated: {len(result['success'])} models")
    for model_id in result['success']:
        logger.info(f"  - {model_id}")
    
    if result['failed']:
        logger.warning(f"❌ Failed to update: {len(result['failed'])} models")
        for failure in result['failed']:
            logger.warning(f"  - {failure['model_id']}: {failure['error']}")


def demo_set_models_group_permissions(client: OpenWebUIClient, model_keyword: str, group_names: List[str]) -> None:
    """Demonstrate setting models to group-based permissions."""
    logger.info("=" * 60)
    logger.info(f"👥 Setting Models with keyword '{model_keyword}' to Group Permissions")
    logger.info(f"Groups: {', '.join(group_names)}")
    logger.info("=" * 60)
    
    result = client.batch_update_model_permissions(
        model_keyword=model_keyword,
        permission_type="group",
        group_identifiers=group_names  # Using group names (will be resolved to IDs)
    )
    
    logger.info(f"✅ Successfully updated: {len(result['success'])} models")
    for model_id in result['success']:
        logger.info(f"  - {model_id}")
    
    if result['failed']:
        logger.warning(f"❌ Failed to update: {len(result['failed'])} models")
        for failure in result['failed']:
            logger.warning(f"  - {failure['model_id']}: {failure['error']}")


def demo_single_model_permission_update(client: OpenWebUIClient, model_id: str) -> None:
    """Demonstrate updating a single model's permissions directly."""
    logger.info("=" * 60)
    logger.info(f"🔧 Updating Single Model '{model_id}' with Custom Access Control")
    logger.info("=" * 60)
    
    # Custom access control with mixed user and group permissions
    custom_access_control = {
        "read": {
            "group_ids": [],  # Will be filled with actual group IDs if available
            "user_ids": []
        },
        "write": {
            "group_ids": [],
            "user_ids": []
        }
    }
    
    # Get groups to populate the access control
    groups = client.list_groups()
    if groups and len(groups) > 0:
        # Use the first group for demonstration
        first_group_id = groups[0]["id"]
        custom_access_control["read"]["group_ids"] = [first_group_id]
        custom_access_control["write"]["group_ids"] = [first_group_id]
        
        updated_model = client.update_model(model_id, access_control=custom_access_control)
        if updated_model:
            logger.info(f"✅ Successfully updated model '{model_id}' with custom permissions")
            logger.info(f"   Read access: groups {custom_access_control['read']['group_ids']}")
            logger.info(f"   Write access: groups {custom_access_control['write']['group_ids']}")
        else:
            logger.error(f"❌ Failed to update model '{model_id}'")
    else:
        logger.warning("No groups available for custom access control demo")


def main() -> None:
    """Demonstrate batch model permissions management."""
    # Validate environment variables
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        return
    
    # Initialize client
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        return
    
    try:
        # Demo 1: List available groups
        groups = demo_list_groups(client)
        
        # Demo 2: List available models to work with
        logger.info("=" * 60)
        logger.info("📋 Listing Available Models")
        logger.info("=" * 60)
        
        models = client.list_models()
        if models and len(models) > 0:
            logger.info(f"Found {len(models)} models:")
            for model in models[:5]:  # Show first 5 models
                logger.info(f"  - {model['id']}")
            if len(models) > 5:
                logger.info(f"  ... and {len(models) - 5} more models")
            
            # Get some model IDs for demonstration
            model_ids_sample = [model['id'] for model in models[:2]]  # First 2 models
            
            # Demo 3: Set specific models to public
            if model_ids_sample:
                demo_set_models_public(client, model_ids_sample)
            
            # Demo 4: Set models with keyword to private (for demonstration, using a common keyword)
            demo_set_models_private(client, "gpt", user_ids=[])  # Empty user_ids for demo
            
            # Demo 5: Set models to group permissions (if groups available)
            if groups and len(groups) > 0:
                group_names = [groups[0]["name"]]  # Use first group
                demo_set_models_group_permissions(client, "claude", group_names)
            
            # Demo 6: Single model update with custom access control
            if model_ids_sample:
                demo_single_model_permission_update(client, model_ids_sample[0])
                
        else:
            logger.warning("No models found or failed to retrieve models")
        
        logger.info("🎉 Batch permissions demo completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Demo execution failed: {e}")


if __name__ == "__main__":
    main()