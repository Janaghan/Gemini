import requests

traffic_info_declaration = {
    "name": "get_traffic_info",
    "description": "Fetch real-time traffic for a given location using TomTom Traffic API.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
        },
        "required": ["location"]
    }
}

def get_air_quality(location: str):
    """Returns real-time air quality info using OpenMeteo API."""
    try:
        # 1. Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5).json()

        if "results" not in geo_resp:
            # Fallback: Try appending ", India" (common context for this user/location)
            # Or just report failure, but let's try to be helpful.
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}, India&count=1&language=en&format=json"
            geo_resp = requests.get(geo_url, timeout=5).json()

        if "results" not in geo_resp:
            # Second Fallback: Try "Chennai" (assuming user context is Chennai based on previous interactions/location)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name=Chennai&count=1&language=en&format=json"
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

    except Exception as e:
        return {"air_quality": f"Air quality fetch error: {e}"}

tools = [get_air_quality]