import os
import sys
import logging
import json
import time
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from openwebui_chat_client import OpenWebUIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AutoTaggerAgent")

def main():
    load_dotenv()
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    token = os.getenv("OUI_AUTH_TOKEN")
    model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4o")

    if not token:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return

    client = OpenWebUIClient(base_url=base_url, token=token, default_model_id=model)
    logger.info("🚀 Auto-Tagger Agent Initialized")

    try:
        # Fetch all recent chats
        logger.info("\n🔍 Step 1: Scanning recent chats for untagged content...")
        recent_chats = client._chat_manager.list_chats()
        
        untagged_chats = []
        for chat in recent_chats:
            chat_id = chat.id if hasattr(chat, 'id') else chat.get('id')
            tags = chat.tags if hasattr(chat, 'tags') else chat.get('tags', [])
            title = chat.title if hasattr(chat, 'title') else chat.get('title', 'Unknown')
            
            if not tags:
                untagged_chats.append({"id": chat_id, "title": title})

        if not untagged_chats:
            logger.info("🎉 All chats are already tagged. Nothing to do!")
            return
            
        logger.info(f"⚠️ Found {len(untagged_chats)} untagged chats. Starting batch processing...\n")

        # Process each untagged chat
        for i, chat_info in enumerate(untagged_chats, 1):
            target_chat_id = chat_info["id"]
            chat_title = chat_info["title"]
            logger.info(f"[{i}/{len(untagged_chats)}] Processing Chat: '{chat_title}' ({target_chat_id})")
            
            # Extract content
            chat_details = client.get_chat(target_chat_id)
            conversation_text = ""
            if chat_details and chat_details.chat and chat_details.chat.history:
                messages = chat_details.chat.history.messages
                for msg in messages.values():
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    conversation_text += f"{role.upper()}: {content}\n\n"
            
            if not conversation_text.strip():
                logger.warning(f"   ⚠️ Chat '{chat_title}' is empty. Skipping.")
                continue

            # Limit text length
            conversation_text = conversation_text[:2000] 

            prompt = f"""
            Analyze the following conversation and provide exactly 3 relevant tags for categorization.
            Respond ONLY with a valid JSON array of strings. Do not include any markdown formatting like ```json.
            Example: ["health", "beverage", "nutrition"]
            
            Conversation:
            {conversation_text}
            """
            
            logger.info("   🧠 Asking AI to generate tags...")
            tag_generation_result = client.chat(question=prompt)
            
            generated_tags = []
            try:
                raw_response = tag_generation_result.content.strip()
                if raw_response.startswith("```json"):
                    raw_response = raw_response[7:]
                if raw_response.startswith("```"):
                    raw_response = raw_response[3:]
                if raw_response.endswith("```"):
                    raw_response = raw_response[:-3]
                    
                generated_tags = json.loads(raw_response.strip())
                logger.info(f"   ✅ Generated tags: {generated_tags}")
            except json.JSONDecodeError:
                logger.error(f"   ❌ Failed to parse AI response as JSON: {tag_generation_result.content}")
                continue

            # Apply tags
            logger.info(f"   ⚡ Solidifying results...")
            success = client.set_chat_tags(target_chat_id, generated_tags)
            
            if success:
                logger.info(f"   🎉 SUCCESS! Tags applied to '{chat_title}'.")
            else:
                logger.error("   ❌ Failed to apply tags to the chat.")
                
            # Sleep briefly to avoid hitting rate limits
            time.sleep(1)

        logger.info("\n🏁 Batch tagging complete! You can now refresh your Open WebUI dashboard.")

    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
