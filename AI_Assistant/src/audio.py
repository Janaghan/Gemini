
import asyncio
import pyaudio
from .tools import handle_tool_call, upload_file
import os

# --- pyaudio config ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

pya = pyaudio.PyAudio()

async def listen_audio(audio_queue_mic, is_assistant_speaking):
    """Listens for audio and puts it into the mic audio queue."""
    mic_info = pya.get_default_input_device_info()
    try:
        audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
    except Exception as e:
        print(f"Microphone Error: {e}")
        return

    kwargs = {"exception_on_overflow": False} if __debug__ else {}
    print(" > Microphone Listening...")
    while True:
        try:
            data = await asyncio.to_thread(audio_stream.read, CHUNK_SIZE, **kwargs)
            
            # ECHO CANCELLATION: Drop input if assistant is speaking
            if is_assistant_speaking.is_set():
                    continue
                    
            await audio_queue_mic.put({"data": data, "mime_type": "audio/pcm"})
        except Exception:
            break

async def send_realtime(session, client, audio_queue_mic, multimodal_queue):
    """Sends audio/text/files from queues to the GenAI session."""
    while True:
        # Prioritize Multimodal Input (Text/Files)
        if not multimodal_queue.empty():
            item = await multimodal_queue.get()
            if "text" in item:
                text = item["text"]
                # Check for commands
                if text.startswith("/add "):
                     # File Upload
                    raw_path = text[5:].strip()
                    file_path = os.path.abspath(os.path.expanduser(raw_path))
                    try:
                        print(f" > Uploading {file_path}...")
                        uploaded_file = await asyncio.to_thread(upload_file, client, file_path)
                        await session.send(input={"file_data": {"file_uri": uploaded_file.uri, "mime_type": uploaded_file.mime_type}}, end_of_turn=True)
                        print(f" > File sent: {file_path}")
                    except Exception as e:
                        print(f" > Error uploading: {e}")
                else:
                    await session.send(input=text, end_of_turn=True)
                    print(f" > Sent text: {text}")
            continue

        # Send Audio
        msg = await audio_queue_mic.get()
        await session.send_realtime_input(audio=msg)

async def receive_audio(session, audio_queue_output):
    """Receives responses from GenAI and puts audio data into the speaker audio queue."""
    while True:
        try:
            turn = session.receive()
            async for response in turn:
                # Token Usage Display
                if response.usage_metadata:
                    print(f" [Token Usage: {response.usage_metadata.total_token_count}]", end="\r")

                if response.tool_call:
                    await handle_tool_call(session, response.tool_call)
                    continue

                if (response.server_content and response.server_content.model_turn):
                    for part in response.server_content.model_turn.parts:
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            audio_queue_output.put_nowait(part.inline_data.data)
                        
                        if part.text:
                            print(f"\nAI: {part.text}")

            # Empty the queue on interruption to stop playback
            while not audio_queue_output.empty():
                audio_queue_output.get_nowait()
        except Exception as e:
            print(f"Receive Error: {e}")
            break

async def play_audio(audio_queue_output, is_assistant_speaking):
    """Plays audio from the speaker audio queue."""
    try:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
    except Exception as e:
        print(f"Speaker Error: {e}")
        return

    print(" > Speaker Ready...")
    while True:
        bytestream = await audio_queue_output.get()
        
        # Mark as speaking
        is_assistant_speaking.set()
        await asyncio.to_thread(stream.write, bytestream)
        
        if audio_queue_output.empty():
            is_assistant_speaking.clear()