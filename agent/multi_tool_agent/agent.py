import datetime
from zoneinfo import ZoneInfo
import requests
from google.adk.agents import Agent


def get_location_data(city_name: str) -> dict:
    """Retrieve location data including timezone and coordinates."""
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city_name}&count=1&language=en&format=json"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]
        return {
            "name": result["name"],
            "timezone": result["timezone"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result["country"],
        }
    except Exception as e:
        print(f"Location error: {e}")
        return None


def get_weather(city: str) -> dict:
    """Get live weather data for a city using Open-Meteo."""
    location = get_location_data(city)

    if not location:
        return {
            "status": "error",
            "error_message": f"Could not find location data for '{city}'.",
        }

    try:
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={location['latitude']}"
            f"&longitude={location['longitude']}"
            "&current_weather=true"
        )

        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

        current = weather_data.get("current_weather")
        if not current:
            raise ValueError("No current weather data")

        report = (
            f"The current weather in {location['name']}, {location['country']} is "
            f"{current['temperature']}°C with wind speed "
            f"{current['windspeed']} km/h."
        )

        return {"status": "success", "report": report}

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch weather data: {str(e)}",
        }


def get_current_time(city: str) -> dict:
    """Get the current local time in a city."""
    location = get_location_data(city)

    if not location or not location.get("timezone"):
        return {
            "status": "error",
            "error_message": f"Could not determine timezone for '{city}'.",
        }

    try:
        tz = ZoneInfo(location["timezone"])
        now = datetime.datetime.now(tz)

        report = (
            f"The current time in {location['name']}, {location['country']} is "
            f"{now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
        )

        return {"status": "success", "report": report}

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Time calculation error: {str(e)}",
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash-lite",
    description="Answers questions about live weather and local time in a city.",
    instruction=(
        "You are a helpful assistant that provides accurate, live weather "
        "and local time information for cities around the world."
    ),
    tools=[get_weather, get_current_time],
)
