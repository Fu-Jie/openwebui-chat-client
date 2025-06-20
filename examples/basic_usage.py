from openwebui_client import OpenWebUIClient

# --- Configuration ---
BASE_URL = "http://localhost:8080"
# It's recommended to use environment variables for sensitive data
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

    if response:
        print(f"AI Response: {response}")

if __name__ == "__main__":
    run_demo()