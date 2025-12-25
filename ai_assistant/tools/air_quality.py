import asyncio
import requests
from google.genai import types

def define_tool():
    """Returns the tool definition for Gemini."""
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_air_quality",
                description="Fetch real-time air quality for a location.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "location": types.Schema(
                            type=types.Type.STRING,
                            description="The city or location."
                        )
                    },
                    required=["location"]
                )
            )
        ]
    )

async def execute(location: str):
    """Fetch AQI data using OpenMeteo."""
    def _fetch():
        try:
            # 1. Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geo_resp = requests.get(geo_url, timeout=5).json()
            if "results" not in geo_resp:
                return {"error": f"Coordinates not found for {location}"}
            
            res = geo_resp["results"][0]
            lat, lon = res["latitude"], res["longitude"]

            # 2. Air Quality
            aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
            aq_resp = requests.get(aq_url, timeout=5).json()
            
            aqi = aq_resp.get("current", {}).get("us_aqi", "Unknown")
            return {"location": location, "aqi": aqi, "status": "Success"}
        except Exception as e:
            return {"error": str(e)}

    return await asyncio.to_thread(_fetch)
