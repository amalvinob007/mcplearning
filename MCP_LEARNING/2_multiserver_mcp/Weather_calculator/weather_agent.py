import os
import requests
from mcp.server.fastmcp import FastMCP
 
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Weather agent")
 
# Weather API configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "http://api.weatherapi.com/v1"
 
 
@mcp.tool()
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    Args:
        location (str): City name, zip code, or coordinates (e.g., "London", "10001", "48.8566,2.3522")
    Returns:
        str: Current weather information including temperature, condition, humidity, and wind
    """
    if not WEATHER_API_KEY:
        return "❌ Weather API key not found. Please set WEATHER_API_KEY environment variable."
    try:
        # Make API request to WeatherAPI
        url = f"{WEATHER_BASE_URL}/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": location,
            "aqi": "no"  # Air quality index not needed for basic weather
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract weather information
            current = data["current"]
            location_info = data["location"]
            weather_report = f"""
🌤️ Weather Report for {location_info['name']}, {location_info['region']}, {location_info['country']}
🌡️ Temperature: {current['temp_c']}°C ({current['temp_f']}°F)
☁️ Condition: {current['condition']['text']}
💨 Wind: {current['wind_kph']} km/h ({current['wind_dir']})
💧 Humidity: {current['humidity']}%
👁️ Visibility: {current['vis_km']} km
🕐 Local Time: {location_info['localtime']}
            """.strip()
            return weather_report
        elif response.status_code == 400:
            return f"❌ Invalid location: {location}. Please check the spelling or try a different format."
        elif response.status_code == 401:
            return "❌ Invalid Weather API key. Please check your WEATHER_API_KEY."
        elif response.status_code == 403:
            return "❌ Weather API access denied. Check your API key permissions."
        else:
            return f"❌ Weather API error: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return "❌ Weather API request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "❌ Unable to connect to weather service. Check your internet connection."
    except Exception as e:
        return f"❌ Error getting weather data: {str(e)}"
 
if __name__ == "__main__":
    mcp.run(transport="stdio")