#!/usr/bin/env python3

import logging
import os
import sys

# Add the client to path
sys.path.insert(0, os.path.abspath('.'))

from openwebui_chat_client import OpenWebUIClient

# Setup logging to catch all messages
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

def test_chat_manager_delegation():
    """Test if chat manager delegation is working properly."""
    try:
        # Create client with skip_model_refresh to avoid connection issues
        client = OpenWebUIClient("http://localhost:3000", "dummy_token", "gpt-4.1", skip_model_refresh=True)
        
        # Get the chat manager
        chat_manager = client._chat_manager
        
        # Test delegation checks
        logger.info("Testing ChatManager delegation...")
        
        # Check if base_client has _parent_client reference
        if hasattr(chat_manager.base_client, '_parent_client'):
            logger.info("✅ base_client has _parent_client reference")
            parent_client = chat_manager.base_client._parent_client
            if parent_client is client:
                logger.info("✅ _parent_client correctly points to main client")
            else:
                logger.error("❌ _parent_client doesn't point to main client")
                return False
        else:
            logger.error("❌ base_client missing _parent_client reference")
            return False
            
        # Check if critical methods exist in parent client
        required_methods = [
            '_find_or_create_chat_by_title', 
            '_ask', 
            'get_folder_id_by_name',
            'create_folder',
            'move_chat_to_folder',
            'set_chat_tags',
            'rename_chat',
            '_upload_file',
            'get_knowledge_base_by_name',
            '_get_knowledge_base_details'
        ]
        
        for method_name in required_methods:
            if hasattr(client, method_name):
                logger.info(f"✅ Client has method: {method_name}")
            else:
                logger.error(f"❌ Client missing method: {method_name}")
                return False
                
        logger.info("✅ All delegation methods exist")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_manager_delegation()
    if success:
        logger.info("🎉 Delegation test passed")
    else:
        logger.error("❌ Delegation test failed")
        sys.exit(1)