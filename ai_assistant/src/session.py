import asyncio
import os
import traceback
import pypdf
from google import genai
from google.genai import types
from websockets.exceptions import ConnectionClosedError
from lmnr import Laminar, observe

# Import tools
from tools import air_quality
from tools import google_search
from src.audio import mic_loop, speaker_loop, shutdown

LIVE_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

# TAG CONSTANTS
TAG_INPUT_TEXT = "\n--input --text "
TAG_INPUT_AUDIO = "\n--input --audio "
TAG_INPUT_PDF = "\n--input --pdf "
TAG_OUTPUT_TEXT = "\n--output --text "
TAG_OUTPUT_AUDIO = "\n--output --audio "

@observe()
async def run_chat_session():
    """Runs the Gemini Live chat session."""
    client = genai.Client(
        api_key=os.environ.get("gemini_api_key"),
        http_options={"api_version": "v1alpha"}
    )
    
    mic_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    interrupt_event = asyncio.Event()
    shutdown_event = asyncio.Event()

    print("🚀 Live AI Assistant (Upgraded Build) starting...")
    
    # Define Tools
    tools = [air_quality.define_tool(), google_search.define_tool()]
    
    # System Instruction: Strictly enforces modality-aware behavior
    sys_instruction = types.Content(parts=[types.Part(text="""
    You are a highly accurate, multimodal AI assistant.
    
    CORE RULES:
    1.  **Text Input**: If the user TYPES text, you MUST respond with a clear, concise TEXT response.
    2.  **Audio Input**: If the user SPEAKS (audio), you MUST respond with a conversational, natural AUDIO response.
    3.  **PDF Analysis**: If the user uploads a PDF, read the provided text context thoroughly and summarize it accurately in TEXT.
    4.  **Accuracy**: Always prioritize factual correctness and direct answers. Do not hallucinate. 
    5.  **Tools**: Use tools whenever external information (weather, search) is needed.
    """)])

    config = {
        "tools": tools, 
        "response_modalities": ["AUDIO"], # Model default modality (can be overridden by text content)
        "system_instruction": sys_instruction
    }

    try:
        print("--- Connecting to Gemini Live ---")
        async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
            print(" Connected")
            print("  Listening... (Speak or Type)")
            
            async with asyncio.TaskGroup() as tg:
                # Audio Tasks (Producer/Consumer)
                tg.create_task(mic_loop(mic_queue, interrupt_event))
                tg.create_task(speaker_loop(output_queue, interrupt_event))
                
                # Session Managers
                tg.create_task(send_loop(session, mic_queue, shutdown_event))
                tg.create_task(receive_loop(session, output_queue, shutdown_event))
                tg.create_task(text_input_loop(session, shutdown_event, mic_queue, interrupt_event))
                
                await shutdown_event.wait()
                
    except asyncio.CancelledError:
        pass
    except ConnectionClosedError as e:
        if "1011" in str(e) or "quota" in str(e).lower():
            print("\n API Quota Exceeded. Please check your billing/quota settings.")
        else:
            print(f"\n Connection Closed: {e}")
            # Optional: Implement auto-reconnect logic here
    except Exception as e:
        print(f" Session Error: {e}")
        traceback.print_exc()
    finally:
        shutdown()

async def text_input_loop(session, shutdown_event, mic_queue, interrupt_event):
    """Handles text input and PDF parsing."""
    try:
        while not shutdown_event.is_set():
            text = await asyncio.to_thread(input)
            if not text:
                continue
            if text.lower() in ["quit", "exit"]:
                shutdown_event.set()
                break
            
            # 1. Interrupt (Stop audio/model output)
            interrupt_event.set()
            
            # 2. Drain Mic (Clear buffer to prevent old audio sending)
            while not mic_queue.empty():
                try: mic_queue.get_nowait()
                except asyncio.QueueEmpty: break
            
            # 3. PDF Detection
            content_to_send = text
            if os.path.isfile(text) and text.lower().endswith(".pdf"):
                print(f"{TAG_INPUT_PDF}📄 Reading PDF: {text}...")
                try:
                    pdf_text = ""
                    reader = pypdf.PdfReader(text)
                    for page in reader.pages:
                        pdf_text += page.extract_text() + "\n"
                    
                    content_to_send = (
                        f"CONTEXT: The user uploaded a PDF named '{text}'. Reading content...\n"
                        f"-- BEGIN PDF CONTENT --\n{pdf_text}\n-- END PDF CONTENT --\n\n"
                        f"USER REQUEST: Please analyze the document above and provide a summary."
                    )
                    print(f"{TAG_INPUT_PDF}Loaded {len(reader.pages)} pages. Context sent.")
                except Exception as e:
                    print(f"[SYSTEM]  Error reading PDF: {e}")
                    continue
            else:
                print(f"{TAG_INPUT_TEXT} You: {text}")

            # Send Text (end_of_turn=True forces model to respond)
            await session.send(input=content_to_send, end_of_turn=True)
            
    except RuntimeError:
        pass 
    except Exception:
        pass

async def send_loop(session, mic_queue, shutdown_event):
    """Streams audio from mic to API."""
    speaking_log_printed = False
    try:
        while not shutdown_event.is_set():
            item = await mic_queue.get()
            
            # If we detect actual speech (filtered by VAD in audio.py), log it once
            if not speaking_log_printed:
                print(f"{TAG_INPUT_AUDIO} User Speaking...", end="", flush=True)
                speaking_log_printed = True
            
            # Send audio chunk
            await session.send(input={"data": item["data"], "mime_type": "audio/pcm"})
            
            # Note: We rely on server-side VAD to detect end of turn for audio
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in send_loop: {e}")

async def receive_loop(session, output_queue, shutdown_event):
    """Receives audio/text from API."""
    audio_log_printed = False
    try:
        while not shutdown_event.is_set():
            async for response in session.receive():
                # 1. Tool Execution
                if response.tool_call:
                    await handle_tool_call(session, response.tool_call)
                
                # 2. Content (Text/Audio)
                if response.server_content:
                    if response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            # Audio
                            if part.inline_data:
                                if not audio_log_printed:
                                    print(f"{TAG_OUTPUT_AUDIO}🔊 AI Speaking...", end="", flush=True)
                                    audio_log_printed = True
                                await output_queue.put(part.inline_data.data)
                            
                            # Text (Transcript or direct text)
                            if part.text:
                                print(f"{TAG_OUTPUT_TEXT}🤖 AI: {part.text}")
                        
                        # Reset audio log trigger on turn completion
                        if response.server_content.turn_complete:
                             audio_log_printed = False

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f" Receive Error: {e}")

@observe(name="handle_tool_call")
async def handle_tool_call(session, tool_call):
    """Executes tools purely functionally."""
    responses = []
    for fc in tool_call.function_calls:
        print(f"\  Tool Triggered: {fc.name} | Args: {fc.args}")
        
        # Dispatch
        result = {"error": "Unknown tool"}
        if fc.name == "get_air_quality":
            result = await air_quality.execute(**fc.args)
        elif fc.name == "google_search":
            result = await google_search.execute(**fc.args)

        responses.append(
            types.FunctionResponse(
                name=fc.name,
                id=fc.id,
                response=result
            )
        )

    # Send result back
    await session.send(
        input=types.LiveClientToolResponse(function_responses=responses)
    )
