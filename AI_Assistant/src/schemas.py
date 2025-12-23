
AIR_QUALITY_SCHEMA = {
    "name": "get_air_quality",
    "description": "Fetch real-time air quality for a given location using OpenMeteo API.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
        },
        "required": ["location"]
    }
}
