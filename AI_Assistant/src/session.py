import os
import asyncio
import threading
import sys
from google import genai
from .tools import get_tool_definitions
# Import the functions from the new audio.py
from .audio import listen_audio, play_audio, send_realtime, receive_audio

# System Instruction
system_instruction = (
    "You are a smart and helpful AI assistant. "
    "Your goal is to provide accurate information using the available tools.\n"
    "**Unbreakable Rule:** You must communicate exclusively in English. Do not switch languages even if the user does."
)

# --- Live API config ---
MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": system_instruction,
    "tools": get_tool_definitions(),
    "generation_config": {
        "max_output_tokens": 2048, # Thinking Budget/Token Limit
    },
    "speech_config": {
        "voice_config": {
            "prebuilt_voice_config": {
                "voice_name": "Aoede"
            }
        }
    }
}

# Queues
audio_queue_output = asyncio.Queue()
audio_queue_mic = asyncio.Queue(maxsize=5)
multimodal_queue = asyncio.Queue()

# Event for Half-Duplex
is_assistant_speaking = asyncio.Event()

def console_input_thread(loop):
    """Reads stdin and puts text into multimodal queue."""
    print(" > Type messages or /add <file> in console.")
    while True:
        try:
            text = sys.stdin.readline()
            if not text:
                 break
            if text.strip():
                asyncio.run_coroutine_threadsafe(multimodal_queue.put({"text": text.strip()}), loop)
        except Exception:
            break

async def run_chat_session():
    """Main function setup."""
    api_key = os.getenv("gemini_api_key")
    if not api_key:
        print("Error: 'gemini_api_key' not found in environment.")
        return

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

    # Start Console Input Thread
    loop = asyncio.get_running_loop()
    threading.Thread(target=console_input_thread, args=(loop,), daemon=True).start()

    try:
        async with client.aio.live.connect(
            model=MODEL, config=CONFIG
        ) as live_session:
            print("Connected to Gemini.")
            print("*** 🎤 MICROPHONE ACTIVE - Start Speaking ***")
            print("*** ⌨️  KEYBOARD ACTIVE - Type anytime ***")
            
            async with asyncio.TaskGroup() as tg:
                # Network Layer (imported from audio.py as requested)
                tg.create_task(send_realtime(live_session, client, audio_queue_mic, multimodal_queue))
                tg.create_task(receive_audio(live_session, audio_queue_output))
                
                # Hardware Layer (imported from audio.py)
                tg.create_task(listen_audio(audio_queue_mic, is_assistant_speaking))
                tg.create_task(play_audio(audio_queue_output, is_assistant_speaking))
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Session Error: {e}")
    finally:
        print("\nSession Closed.")