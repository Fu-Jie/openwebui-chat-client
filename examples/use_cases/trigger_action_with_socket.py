import os
import sys
import asyncio
import socketio
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from openwebui_chat_client import AsyncOpenWebUIClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ActionSocket")

async def main():
    load_dotenv()
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    token = os.getenv("OUI_AUTH_TOKEN")
    model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4o")

    if not token:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return

    # 1. Initialize Async Client
    client = AsyncOpenWebUIClient(base_url=base_url, token=token, default_model_id=model)
    
    # 2. Setup Socket.IO Client to intercept events
    sio = socketio.AsyncClient(logger=True, engineio_logger=True)
    
    @sio.on('connect')
    async def on_connect():
        logger.info(f"🔌 Socket connected! Session ID: {sio.sid}")

    @sio.on('events')
    async def on_events(data):
        event_type = data.get("data", {}).get("type", "unknown")
        logger.info(f"📥 Received Broadcast Event (__event_emitter__): {event_type}")
        if event_type == "message":
            content = data.get("data", {}).get("data", {}).get("content", "")
            logger.info(f"   [Appended Content]: {content}")

    # Listen for direct calls (__event_call__)
    @sio.on('execute')
    async def on_execute(data):
        logger.info(f"⚡ Received Direct Execute Event (__event_call__)!")
        code = data.get("code", "")
        logger.info(f"   [JS Code to run in browser]: {code[:200]}...")
        return {"status": "success"} # Acknowledge the call

    # The backend might send the execute directly to 'events' with type 'execute' depending on version
    # So we catch all 'events' and parse them:
    @sio.on('*')
    async def catch_all(event, data):
        if event not in ['events', 'execute']:
            logger.info(f"👀 Caught other event: {event}")

    try:
        # Connect to Open WebUI Socket server using standard HTTP URL (Socket.IO handles the upgrade)
        await sio.connect(base_url, socketio_path="/ws/socket.io", transports=['websocket'], auth={"token": token})
        
        session_id = sio.sid

        # 3. Create a chat
        logger.info("\n💬 Initiating chat...")
        result = await client.chat(
            question="Briefly explain Quantum entanglement.",
            chat_title="Socket Action Test"
        )
        chat_id = result.chat_id
        message_id = result.message_id
        logger.info(f"✅ Chat ID: {chat_id}")

        # 4. Trigger Action using OUR REAL session_id
        target_action_id = "smart_mind_map"
        logger.info(f"\n🚀 Triggering Action '{target_action_id}' using Session ID: {session_id}")
        
        # We fetch history to provide context
        chat_details = await client.get_chat(chat_id)
        messages_dict = chat_details.chat.history.messages if chat_details.chat and chat_details.chat.history else {}
        messages = [m.model_dump() for m in messages_dict.values()]

        await client.trigger_action(
            action_id=target_action_id,
            chat_id=chat_id,
            message_id=message_id,
            params={
                "messages": messages,
                "session_id": session_id  # <--- The Magic Key
            }
        )
        
        logger.info("⏳ Waiting 10 seconds to receive all socket events...")
        await asyncio.sleep(10)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await sio.disconnect()
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
