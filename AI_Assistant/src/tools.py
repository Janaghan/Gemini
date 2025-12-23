
import requests
import asyncio
import os
import mimetypes
from google.genai import types
from lmnr import observe
from .schemas import AIR_QUALITY_SCHEMA

# Tool Definitions
def get_tool_definitions():
    """Returns a list of all tool definitions correctly formatted for LiveConnectConfig."""
    
    # Air Quality Tool Declaration
    aq_tool_decl = types.FunctionDeclaration(
        name=AIR_QUALITY_SCHEMA["name"],
        description=AIR_QUALITY_SCHEMA["description"],
        parameters=types.Schema(
             type=types.Type.OBJECT,
             properties={
                 "location": types.Schema(
                     type=types.Type.STRING,
                     description="The location to get air quality for."
                 )
             },
             required=["location"]
        )
    )

    # Wrap in Tool object
    aq_tool = types.Tool(function_declarations=[aq_tool_decl])
    
    # Google Search Tool
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    return [aq_tool, google_search_tool]

def upload_file(client, file_path: str):
    """
    Uploads a file to Gemini.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # Fallback for common types if mimetypes fails or returns None
        if file_path.endswith(".txt"):
            mime_type = "text/plain"
        elif file_path.endswith(".pdf"):
            mime_type = "application/pdf"
        elif file_path.endswith(".wav"):
            mime_type = "audio/wav"
        else:
            mime_type = "application/pdf" # Default to PDF if unknown

    print(f"Uploading {file_path} as {mime_type}...")
    with open(file_path, "rb") as f:
        uploaded_file = client.files.upload(
            file=f,
            config=dict(mime_type=mime_type)
        )
    
    print(f"File uploaded: {uploaded_file.name}")
    return uploaded_file

# Tool Implementations
@observe()
async def get_air_quality(location: str):
    """Returns real-time air quality info using OpenMeteo API."""
    print(f"Tool Action: Fetching Air Quality for {location}")
    try:
        # Run blocking requests in a thread to avoid blocking the asyncio loop
        def _fetch():
            # 1. Get coordinates
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_resp = requests.get(geo_url, timeout=5).json()

            if "results" not in geo_resp:
                # Fallback: Try appending ", India"
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}, India&count=1&language=en&format=json"
                geo_resp = requests.get(geo_url, timeout=5).json()

            if "results" not in geo_resp:
                 return {"air_quality": f"Could not find coordinates for {location}."}

            lat = geo_resp["results"][0]["latitude"]
            lon = geo_resp["results"][0]["longitude"]

            # 2. Get Air Quality
            aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5"
            aq_resp = requests.get(aq_url, timeout=5).json()

            if "current" not in aq_resp:
                return {"air_quality": f"No air quality data available for {location}."}

            current = aq_resp["current"]
            aqi = current["us_aqi"]
            pm25 = current["pm2_5"]
            
            # Determine category
            category = "Good"
            if aqi > 50: category = "Moderate"
            if aqi > 100: category = "Unhealthy for Sensitive Groups"
            if aqi > 150: category = "Unhealthy"
            if aqi > 200: category = "Very Unhealthy"
            if aqi > 300: category = "Hazardous"

            return {"air_quality": f"Air Quality in {location}: AQI {aqi} ({category}), PM2.5: {pm25} µg/m³"}

        return await asyncio.to_thread(_fetch)

    except Exception as e:
        return {"air_quality": f"Air quality fetch error: {e}"}

# Tool Execution Logic
async def handle_tool_call(session, tool_call):
    """
    Handles income tool calls from the Live API.
    Routes calls to the appropriate function and sends response.
    """
    for fc in tool_call.function_calls:
        name = fc.name
        args = fc.args
        result = {}

        if name == "get_air_quality":
            result = await get_air_quality(**args)
        else:
            print(f"Warning: Unknown tool call {name}")
            continue

        # Send response back
        await session.send(
            input=types.LiveClientToolResponse(
                function_responses=[
                    types.FunctionResponse(
                        name=name,
                        id=fc.id,
                        response=result
                    )
                ]
            ),
            end_of_turn=False
        )