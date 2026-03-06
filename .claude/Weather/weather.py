"""
weather.py - A simple script to fetch weather data using the OpenWeatherMap API.

Python concepts demonstrated:
  - Variables and data types
  - Functions
  - HTTP requests with the `requests` library
  - Dictionaries (JSON parsing)
  - String formatting (f-strings)
  - Error handling (try/except)
  - User input
"""

import requests  # Third-party library for making HTTP requests

# --- CONFIGURATION ---
# Sign up for a free API key at: https://openweathermap.org/api
API_KEY = "28afea803ade1b0216095ee2de925659"
BASE_URL = "https://api.openweathermap.org/data/3.0/weather"


def get_weather(city: str) -> dict:
    """
    Fetch current weather for a given city.

    Args:
        city: Name of the city (e.g. "London" or "New York")

    Returns:
        A dictionary with weather details, or None if the request fails.
    """
    # Build query parameters as a Python dictionary
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",   # Use "imperial" for Fahrenheit
    }

    # Make the HTTP GET request
    response = requests.get(BASE_URL, params=params)

    # HTTP 200 means success; any other code means something went wrong
    if response.status_code == 200:
        return response.json()  # Parse the JSON body into a Python dict
    elif response.status_code == 401:
        print("Error: Invalid API key. Check your API_KEY value.")
    elif response.status_code == 404:
        print(f"Error: City '{city}' not found.")
    else:
        print(f"Error: Received status code {response.status_code}")

    return None


def display_weather(data: dict) -> None:
    """
    Print weather information in a human-readable format.

    Args:
        data: The parsed JSON dictionary returned by the API.
    """
    # Navigate the nested dictionary to extract values
    city_name    = data["name"]
    country      = data["sys"]["country"]
    description  = data["weather"][0]["description"].capitalize()
    temp         = data["main"]["temp"]
    feels_like   = data["main"]["feels_like"]
    humidity     = data["main"]["humidity"]
    wind_speed   = data["wind"]["speed"]

    # f-strings let you embed variables directly inside strings
    print("\n" + "=" * 35)
    print(f"  Weather in {city_name}, {country}")
    print("=" * 35)
    print(f"  Condition : {description}")
    print(f"  Temp      : {temp}°C  (feels like {feels_like}°C)")
    print(f"  Humidity  : {humidity}%")
    print(f"  Wind      : {wind_speed} m/s")
    print("=" * 35 + "\n")


def main():
    """Entry point of the script."""
    # input() pauses execution and waits for the user to type something
    city = input("Enter a city name: ").strip()

    if not city:
        print("No city entered. Exiting.")
        return

    # try/except catches errors so the script doesn't crash unexpectedly
    try:
        weather_data = get_weather(city)
        if weather_data:
            display_weather(weather_data)
    except requests.exceptions.ConnectionError:
        print("Error: No internet connection.")
    except Exception as e:
        print(f"Unexpected error: {e}")


# This block only runs when the file is executed directly,
# not when it's imported as a module by another script.
if __name__ == "__main__":
    main()
