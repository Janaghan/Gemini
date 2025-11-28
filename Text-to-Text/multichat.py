import time
from google.genai import types
from config import client
from log_setup import log_multichat   # <-- updated name


def multichat():
    # Create chat session
    chat = client.chats.create(model="gemini-2.5-flash")

    def get_input(user_message):

        start_time = time.time()

        # Log request
        request_record = {
            "event": "request",
            "type": "chat",
            "input_message": user_message,
            "model": "gemini-2.5-flash",
            "timestamp": time.time(),
        }
        log_multichat(request_record)

        # Send message to Gemini chat session
        response = chat.send_message(user_message)

        end_time = time.time()

        # Log response
        response_record = {
            "event": "response",
            "type": "chat",
            "input_message": user_message,
            "response_text": response.text,
            "latency_ms": round((end_time - start_time) , 2),
            # "timestamp": time.time(),
        }
        log_multichat(response_record)

        print("\nMODEL:", response.text)
        return response

    print("USER: I have 2 dogs in my house.")
    get_input("I have 2 dogs in my house.")

    print("\nUSER: How many paws are in my house?")
    get_input("How many paws are in my house?")

    print("\n--- CHAT HISTORY ---\n")

    # Iterate over chat history
    for msg in chat.get_history():

        role = msg.role
        parts = msg.parts[0].text if msg.parts else ""

        # Log each history event
        history_record = {
            "event": "CHAT_HISTORY",
            "role": role,
            "message": parts,
            "timestamp": time.time()
        }
        log_multichat(history_record)

        print(f"{role}: {parts}")


# Run example
multichat()
