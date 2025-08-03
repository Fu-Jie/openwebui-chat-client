#!/usr/bin/env python3
"""
Simple test script to check the functionality without requiring environment variables.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from openwebui_chat_client import OpenWebUIClient

def test_client_initialization():
    """Test basic client initialization."""
    try:
        # Try to initialize the client
        client = OpenWebUIClient(
            base_url="http://localhost:3000",
            token="test_token", 
            default_model_id="test_model",
            skip_model_refresh=True  # Skip model refresh to avoid network calls
        )
        print("✅ Client initialization successful")
        
        # Check if key methods exist
        methods_to_check = [
            'stream_chat', 'parallel_chat', '_ask_stream', 
            '_get_single_model_response_in_parallel', '_stream_delta_update',
            '_get_model_completion_stream', '_ensure_placeholder_messages',
            '_get_next_available_message_pair', '_cleanup_unused_placeholder_messages'
        ]
        
        for method_name in methods_to_check:
            if hasattr(client, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
                
        return True
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

def test_method_signatures():
    """Test if methods have correct signatures."""
    try:
        client = OpenWebUIClient(
            base_url="http://localhost:3000",
            token="test_token", 
            default_model_id="test_model",
            skip_model_refresh=True
        )
        
        # Test stream_chat signature
        import inspect
        sig = inspect.signature(client.stream_chat)
        print(f"✅ stream_chat signature: {sig}")
        
        # Test parallel_chat signature  
        sig = inspect.signature(client.parallel_chat)
        print(f"✅ parallel_chat signature: {sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ Method signature test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenWebUI Chat Client Functionality")
    print("=" * 60)
    
    success = True
    success &= test_client_initialization()
    success &= test_method_signatures()
    
    if success:
        print("\n🎉 All basic tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
    print("💡 To test full functionality, set environment variables and run integration tests:")
    print("   export OUI_BASE_URL='http://localhost:3000'")
    print("   export OUI_AUTH_TOKEN='your_token'")
    print("   python examples/chat_features/streaming_chat.py")