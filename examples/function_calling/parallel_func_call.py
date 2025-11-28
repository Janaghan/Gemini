import json
import time

from google.genai import Client, types  
from log_setup import log_parallel_function_calling
from config import client

power_disco_ball = {
    "name": "power_disco_ball",
    "description": "Powers the spinning disco ball.",
    "parameters": {
        "type": "object",
        "properties": {
            "power": {
                "type": "boolean",
                "description": "Whether to turn the disco ball on or off.",
            }
        },
        "required": ["power"],
    },
}

start_music = {
    "name": "start_music",
    "description": "Play some music matching the specified parameters.",
    "parameters": {
        "type": "object",
        "properties": {
            "energetic": {
                "type": "boolean",
                "description": "Whether the music is energetic or not.",
            },
            "loud": {
                "type": "boolean",
                "description": "Whether the music is loud or not.",
            },
        },
        "required": ["energetic", "loud"],
    },
}

dim_lights = {
    "name": "dim_lights",
    "description": "Dim the lights.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "number",
                "description": "The brightness of the lights, 0.0 is off, 1.0 is full.",
            }
        },
        "required": ["brightness"],
    },
}


def parallel_function_calling(prompt):
    start_time = time.time()

    model = "gemini-2.5-flash"
    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        # "timestamp": time.time(),
    }
    log_parallel_function_calling(request_record)


    house_tools = [
        types.Tool(function_declarations=[power_disco_ball, start_music, dim_lights])
    ]
    # config = types.GenerateContentConfig(
    # tools=[power_disco_ball_impl, start_music_impl, dim_lights_impl]
    #   )  ##### For Automatic Function calling #####3

    config = types.GenerateContentConfig(
        tools=house_tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        # Force the model to call 'any' function, instead of chatting.
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    )

    chat = client.chats.create(model=model, config=config)
    response = chat.send_message(prompt)

    # Print out each of the function calls requested from this single call
    print("Example 1: Forced function calling")
    for fn in response.function_calls:
        args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
        print(f"{fn.name}({args})")
    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2),
        # "timestamp": time.time(),
    }
    log_parallel_function_calling(response_record)

    return response.text


# Example Usage
answer = parallel_function_calling("Turn this place into a party!")

print("Answer", answer)
