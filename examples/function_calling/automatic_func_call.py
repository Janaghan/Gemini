import json
import time
from google.genai import types           # correct import
from config import client                 # your Gemini client
from log_setup import log_automatic_function_calling   # your logger


def power_disco_ball_impl(power: bool) -> dict:
    """Powers the spinning disco ball.

    Args:
        power: Whether to turn the disco ball on or off.

    Returns:
        A status dictionary indicating the current state.
    """
    return {"status": f"Disco ball powered {'on' if power else 'off'}"}

def start_music_impl(energetic: bool, loud: bool) -> dict:
    """Play some music matching the specified parameters.

    Args:
        energetic: Whether the music is energetic or not.
        loud: Whether the music is loud or not.

    Returns:
        A dictionary containing the music settings.
    """
    music_type = "energetic" if energetic else "chill"
    volume = "loud" if loud else "quiet"
    return {"music_type": music_type, "volume": volume}

def dim_lights_impl(brightness: float) -> dict:
    """Dim the lights.

    Args:
        brightness: The brightness of the lights, 0.0 is off, 1.0 is full.

    Returns:
        A dictionary containing the new brightness setting.
    """
    return {"brightness": brightness}

def automatic_function_calling(prompt):

    start_time = time.time()
    model = "gemini-2.5-flash"


    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        # "timestamp": time.time(),
    }
    log_automatic_function_calling(request_record)

    # Actual function implementations

    config = types.GenerateContentConfig(
        tools=[power_disco_ball_impl, start_music_impl, dim_lights_impl]
    )

    # Make the request
    response = client.models.generate_content(
        model=model,
        contents="Do everything you need to this place into party!",
        config=config,
    )


    end_time = time.time()
    
    # Log each streamed chunk
    response_record = {
        "event": "response",
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2),
    }

    

    log_automatic_function_calling(response_record)

    return response.text


# Example usage
answer = automatic_function_calling("Do everything you need to this place into party!")
print("Answer", answer)
