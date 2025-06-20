from openwebui_chat_client import OpenWebUIClient

# --- Configuration ---
BASE_URL = "http://localhost:3000"  # Replace with your OpenWebUI server URL
# Obtain your JWT token or API key for authentication from your account settings.
AUTH_TOKEN = "YOUR_AUTH_TOKEN" 
MODEL_ID = "gpt-4.1"

def run_demo():
    """Demonstrates the basic functionality of the OpenWebUIClient."""
    if AUTH_TOKEN == "YOUR_AUTH_TOKEN":
        print("🛑 Please set your 'AUTH_TOKEN' in the script.")
        return
        
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, MODEL_ID)

    # Start or continue a conversation
    response, message_id = client.chat(
        question="What are the key principles of object-oriented programming?",
        chat_title="OOP Principles Discussion"
    )
    
    # continue the conversation with a follow-up question
    if message_id:
        print(f"Message ID: {message_id}")
    response, _ = client.chat(
        question="Can you explain encapsulation in more detail?",
        chat_title="OOP Principles Discussion",
    )

    if response:
        print(f"AI Response: {response}")

if __name__ == "__main__":
    run_demo()