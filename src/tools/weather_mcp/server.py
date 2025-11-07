import httpx
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from src.config import settings

mcp = FastMCP("Weather")

WEATHER_API_KEY = settings.weather_config.api_key
WEATHER_API_BASE_URL = settings.weather_config.base_url


def _fetch_current_weather(location: str) -> dict:
    """Helper function to fetch current weather data from API."""
    if not WEATHER_API_KEY:
        return {"error": "API key not found"}
    
    weather_api_url = f"{WEATHER_API_BASE_URL}/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "aqi": "yes",
    }
    
    try:
        response = httpx.get(weather_api_url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}


def _fetch_astronomy_data(location: str, date: str = None) -> dict:
    """Helper function to fetch astronomy data from API."""
    if not WEATHER_API_KEY:
        return {"error": "API key not found"}
    
    # Use today's date if not provided, in yyyy-MM-dd format
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    astronomy_api_url = f"{WEATHER_API_BASE_URL}/astronomy.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "dt": date,
    }
    
    try:
        response = httpx.get(astronomy_api_url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch astronomy: {str(e)}"}


@mcp.tool()
def get_current_weather(location: str) -> dict:
    """
    Get current weather and wind information for a given location.
    
    Args:
        location: The city name or location (e.g., "New York", "London", "Tehran")
    
    Returns:
        A dictionary containing:
        - Temperature in Celsius and feels-like temperature in Celsius
        - Weather condition description (e.g., "Partly cloudy", "Clear")
        - Wind speed in kilometers per hour (kph)
        - Wind direction as compass point (e.g., "N", "SE", "WSW")
        - Wind degree (0-360, where 0 is North)
        - Whether it's currently day or night (1 for day, 0 for night)
        - Location details: name, region, country, and local time
    """
    data = _fetch_current_weather(location)
    if not data or "error" in data:
        return data or {"error": "Failed to fetch weather data"}
    
    current = data.get("current", {})
    location_data = data.get("location", {})
    condition = current.get("condition", {})
    
    return {
        "location": {
            "name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "localtime": location_data.get("localtime"),
        },
        "weather": {
            "temperature_c": current.get("temp_c"),
            "feels_like_c": current.get("feelslike_c"),
            "condition": condition.get("text"),
            "is_day": current.get("is_day"),
        },
        "wind": {
            "speed_kph": current.get("wind_kph"),
            "direction": current.get("wind_dir"),
            "degree": current.get("wind_degree"),
        },
    }


@mcp.tool()
def get_current_atmospheric_conditions(location: str) -> dict:
    """
    Get current atmospheric conditions for a given location.
    
    Args:
        location: The city name or location (e.g., "New York", "London", "Tehran")
    
    Returns:
        A dictionary containing:
        - Humidity as percentage (0-100)
        - Atmospheric pressure in millibars (mb)
        - Cloud cover as percentage (0-100)
        - Visibility distance in kilometers
        - Precipitation amount in millimeters
        - UV index (typically 0-11+, where higher values indicate stronger UV radiation)
        - Dew point in Celsius
        - Location details: name, region, country, and local time
    """
    data = _fetch_current_weather(location)
    if not data or "error" in data:
        return data or {"error": "Failed to fetch weather data"}
    
    current = data.get("current", {})
    location_data = data.get("location", {})
    
    return {
        "location": {
            "name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "localtime": location_data.get("localtime"),
        },
        "atmospheric_conditions": {
            "humidity_percent": current.get("humidity"),
            "pressure_mb": current.get("pressure_mb"),
            "cloudcover_percent": current.get("cloud"),
            "visibility_km": current.get("vis_km"),
            "precipitation_mm": current.get("precip_mm"),
            "uv_index": current.get("uv"),
            "dewpoint_c": current.get("dewpoint_c"),
        },
    }


@mcp.tool()
def get_current_astronomical_data(location: str) -> dict:
    """
    Get current astronomical data for a given location.
    
    Args:
        location: The city name or location (e.g., "New York", "London", "Tehran")
    
    Returns:
        A dictionary containing:
        - Sunrise and sunset times in local time format (e.g., "06:30 AM")
        - Moonrise and moonset times in local time format (e.g., "08:45 PM")
        - Moon phase (e.g., "Waxing Crescent", "Full Moon", "Waning Gibbous")
        - Moon illumination as percentage (0-100)
        - Whether the sun is currently up (1 for yes, 0 for no)
        - Whether the moon is currently up (1 for yes, 0 for no)
        - Location details: name, region, country, and local time
    """
    data = _fetch_astronomy_data(location)
    if not data or "error" in data:
        return data or {"error": "Failed to fetch astronomy data"}
    
    location_data = data.get("location", {})
    astro_data = data.get("astronomy", {}).get("astro", {})
    
    return {
        "location": {
            "name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "localtime": location_data.get("localtime"),
        },
        "sun": {
            "sunrise": astro_data.get("sunrise"),
            "sunset": astro_data.get("sunset"),
            "is_sun_up": astro_data.get("is_sun_up"),
        },
        "moon": {
            "moonrise": astro_data.get("moonrise"),
            "moonset": astro_data.get("moonset"),
            "phase": astro_data.get("moon_phase"),
            "illumination_percent": astro_data.get("moon_illumination"),
            "is_moon_up": astro_data.get("is_moon_up"),
        },
    }


@mcp.tool()
def get_current_air_quality(location: str) -> dict:
    """
    Get current air quality data for a given location.
    
    Args:
        location: The city name or location (e.g., "New York", "London", "Tehran")
    
    Returns:
        A dictionary containing pollutant levels in micrograms per cubic meter (μg/m³):
        - CO (Carbon Monoxide)
        - NO2 (Nitrogen Dioxide)
        - O3 (Ozone)
        - SO2 (Sulfur Dioxide)
        - PM2.5 (Fine Particulate Matter, particles ≤ 2.5 micrometers)
        - PM10 (Coarse Particulate Matter, particles ≤ 10 micrometers)
        - US EPA Air Quality Index (1-6 scale: 1=Good, 2=Moderate, 3=Unhealthy for Sensitive Groups, 4=Unhealthy, 5=Very Unhealthy, 6=Hazardous)
        - UK DEFRA Air Quality Index (1-10 scale: 1-3=Low, 4-6=Moderate, 7-9=High, 10=Very High)
        - Location details: name, region, country, and local time
    """
    data = _fetch_current_weather(location)
    if not data or "error" in data:
        return data or {"error": "Failed to fetch weather data"}
    
    current = data.get("current", {})
    location_data = data.get("location", {})
    air_quality = current.get("air_quality", {})
    
    return {
        "location": {
            "name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "localtime": location_data.get("localtime"),
        },
        "pollutants": {
            "co_carbon_monoxide_ug_m3": air_quality.get("co"),
            "no2_nitrogen_dioxide_ug_m3": air_quality.get("no2"),
            "o3_ozone_ug_m3": air_quality.get("o3"),
            "so2_sulfur_dioxide_ug_m3": air_quality.get("so2"),
        },
        "particulate_matter": {
            "pm2_5_ug_m3": air_quality.get("pm2_5"),
            "pm10_ug_m3": air_quality.get("pm10"),
        },
        "air_quality_index": {
            "us_epa_index": air_quality.get("us-epa-index"),
            "gb_defra_index": air_quality.get("gb-defra-index"),
        },
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")