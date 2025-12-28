import asyncio
import pyaudio
import sys
import ctypes
import math
import struct
import collections

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
MIC_RATE = 16000     # 16kHz Input
SPEAKER_RATE = 24000 # 24kHz Output
CHUNK_SIZE = 4096

# VAD Configuration
THRESHOLD_START = 800   # RMS to start sending
THRESHOLD_STOP = 400    # RMS to stop sending (Hysteresis)
PRE_ROLL_CHUNKS = 5     # Keep ~1s of audio before trigger

# Suppress ALSA/Jack Logs
try:
    ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = ctypes.cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except Exception:
    pass

pya = pyaudio.PyAudio()

def calculate_rms(data):
    """Calculates RMS amplitude of audio chunk."""
    if not data:
        return 0
    count = len(data) // 2
    format = "<%dh" % count
    shorts = struct.unpack(format, data)
    sum_squares = sum(s * s for s in shorts)
    return math.sqrt(sum_squares / count)

async def mic_loop(mic_queue, interrupt_event):
    """
    Captures audio with Hysteresis VAD and Pre-roll buffering.
    """
    stream = await asyncio.to_thread(
        pya.open,
        format=FORMAT,
        channels=CHANNELS,
        rate=MIC_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )
    
    # Pre-roll buffer to catch the start of words
    pre_roll_buffer = collections.deque(maxlen=PRE_ROLL_CHUNKS)
    is_speaking = False
    
    try:
        while True:
            # Handle Interrupts (e.g., user requests stop)
            if interrupt_event.is_set():
                is_speaking = False
                pre_roll_buffer.clear()
                await asyncio.sleep(0.1)
                continue
                
            try:
                data = await asyncio.to_thread(stream.read, CHUNK_SIZE, exception_on_overflow=False)
                rms = calculate_rms(data)
                
                # Logic: State Machine for VAD
                if is_speaking:
                    # Check if we should STOP
                    if rms < THRESHOLD_STOP:
                        # Potential silence, but maybe just a pause?
                        # For simplicity, we cut immediately if below STOP threshold, 
                        # relying on the low value of STOP to handle pauses.
                        is_speaking = False
                        # print("DEBUG: Silence detected, stopping stream.")
                    else:
                        # Continue sending
                        await mic_queue.put({"data": data, "mime_type": "audio/pcm"})

                else:
                    # Check if we should START
                    if rms > THRESHOLD_START:
                        is_speaking = True
                        # Flush pre-roll first
                        while pre_roll_buffer:
                            await mic_queue.put({"data": pre_roll_buffer.popleft(), "mime_type": "audio/pcm"})
                        # Send current chunk
                        await mic_queue.put({"data": data, "mime_type": "audio/pcm"})
                    else:
                        # Just buffer updates
                        pre_roll_buffer.append(data)
                        
            except OSError:
                await asyncio.sleep(0.1)
                continue
                
    except asyncio.CancelledError:
        pass
    finally:
        if stream.is_active():
            stream.stop_stream()
        stream.close()

async def speaker_loop(output_queue, interrupt_event):
    """
    Plays audio from queue.
    """
    stream = await asyncio.to_thread(
        pya.open,
        format=FORMAT,
        channels=CHANNELS,
        rate=SPEAKER_RATE,
        output=True,
    )
    
    try:
        while True:
            # Drain if interrupted
            if interrupt_event.is_set():
                while not output_queue.empty():
                    try:
                        output_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                interrupt_event.clear()
            
            item = await output_queue.get()
            if item is None:
                break
            
            try:
                await asyncio.to_thread(stream.write, item)
            except OSError:
                pass

    except asyncio.CancelledError:
        pass
    finally:
        if stream.is_active():
            stream.stop_stream()
        stream.close()

def shutdown():
    pya.terminate()
