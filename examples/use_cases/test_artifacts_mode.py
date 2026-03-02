import os
import sys
import logging
import time
import uuid
import re
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.models import ChatResponse, ActionResult

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ArtifactsTest")

def main():
    load_dotenv()
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    token = os.getenv("OUI_AUTH_TOKEN")
    model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4o")

    if not token:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return

    client = OpenWebUIClient(base_url=base_url, token=token, default_model_id=model)
    
    unique_suffix = str(uuid.uuid4())[:8]
    test_title = f"Artifacts Mode Test {unique_suffix}"

    try:
        # 1. Start a chat
        logger.info(f"\n💬 Step 1: Requesting an Artifact-ready application...")
        question = """Create a beautiful, interactive Digital Clock using HTML, CSS, and JavaScript. 
        Provide the complete code in a single HTML block. 
        Ensure it has a dark theme and some smooth animations."""
        
        result: ChatResponse = client.chat(
            question=question,
            chat_title=test_title
        )

        if not result or not result.content:
            logger.error("❌ Failed to get response")
            return

        chat_id = result.chat_id
        message_id = result.message_id
        logger.info(f"✅ Chat completed. Chat ID: {chat_id}")

        # 2. Extract content
        html_match = re.search(r"```html\s*(.*?)\s*```", result.content, re.DOTALL)
        html_content = html_match.group(1) if html_match else result.content

        # 3. Simulate Artifact injection
        logger.info(f"\n📦 Step 2: Manually enriching message with Artifact metadata...")
        
        artifact_embed = {
            "type": "artifact",
            "data": {
                "title": "Digital Clock",
                "content": html_content,
                "language": "html"
            }
        }

        # 4. Synchronize
        logger.info("📡 Pushing Artifact to database...")
        chat_data = client._base_client._get_json_response("GET", f"/api/v1/chats/{chat_id}")
        chat_obj = chat_data.get("chat", {})
        history = chat_obj.get("history", {})
        messages = history.get("messages", {})
        
        if message_id in messages:
            msg = messages[message_id]
            msg["embeds"] = msg.get("embeds", []) + [artifact_embed]
            
            update_payload = {
                "chat": {
                    **chat_obj,
                    "title": test_title,
                    "history": {
                        **history,
                        "messages": messages
                    }
                }
            }
            
            client.session.post(
                f"{base_url}/api/v1/chats/{chat_id}",
                headers=client.json_headers,
                json=update_payload
            ).raise_for_status()
            
            logger.info(f"🎉 Artifact injected! Title: '{test_title}'")
            logger.info(f"🏁 Please check your browser. Look for the Artifacts panel on the right.")
        else:
            logger.error("❌ Target message not found for injection.")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
