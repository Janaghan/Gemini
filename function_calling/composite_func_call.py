import json
import time

from google.genai import types
from config import client
from log_setup import log_composite_function_calling
import os
from google import genai
from google.genai import types

# Example Functions
def get_weather_forecast(location: str) -> dict:
    """Gets the current weather temperature for a given location."""
    print(f"Tool Call: get_weather_forecast(location={location})")
    # TODO: Make API call
    print("Tool Response: {'temperature': 25, 'unit': 'celsius'}")
    return {"temperature": 25, "unit": "celsius"}  # Dummy response

def set_thermostat_temperature(temperature: int) -> dict:
    """Sets the thermostat to a desired temperature."""
    print(f"Tool Call: set_thermostat_temperature(temperature={temperature})")
    # TODO: Interact with a thermostat API
    print("Tool Response: {'status': 'success'}")
    return {"status": "success"}


def thinking_streaming(prompt):
    start_time = time.time()
    model = "gemini-2.5-flash"
    include_thoughts=True
    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "config": {
            "include_thoughts": include_thoughts
        },
        "timestamp": time.time(),
    }
    log_composite_function_calling(request_record)

    config = types.GenerateContentConfig(
    tools=[get_weather_forecast, set_thermostat_temperature]
    )

    # Make the request
    response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=config,
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    log_composite_function_calling(response_record)

    return response.text


# Run example
answer = thinking_streaming("If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise set it to 18°C.")
print("\nFINAL ANSWER:\n", answer)
