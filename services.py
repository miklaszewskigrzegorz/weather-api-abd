from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os
import logging
from models import WeatherRequest
from database import WeatherData

# Load environment variables from the .env file
load_dotenv()

# Fetch the API key from the environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is missing. Please ensure it is set in the .env file.")

# Base URLs for different weather data types
BASE_URL_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
BASE_URL_HISTORICAL = "https://api.openweathermap.org/data/2.5/onecall/timemachine"

# Configure logging
logging.basicConfig(level=logging.INFO)


def fetch_weather_data(request: WeatherRequest):
    """
    Fetch weather data based on the request type (current, forecast, or historical).

    Parameters:
        request (WeatherRequest): Input request containing city, country, and date range.

    Returns:
        List[WeatherData]: Weather data objects for the requested type.
    """
    logging.info(f"Fetching weather data for request: {request}")

    if not request.city or not request.country:
        raise ValueError("City and country must be provided.")

    # Determine the request type
    if request.start_date and request.end_date:
        # Handle historical data
        return fetch_historical_weather(request)
    elif request.start_date is None and request.end_date is None:
        # Handle current data
        return fetch_current_weather(request)
    else:
        # Handle forecast data
        return fetch_forecast_weather(request)


def fetch_current_weather(request: WeatherRequest):
    """
    Fetch current weather data.
    """
    # Prepare query parameters
    params = {
        "q": f"{request.city},{request.country}" if request.city and request.country else None,
        "zip": f"{request.postal_code},{request.country}" if request.postal_code else None,
        "appid": API_KEY,
        "units": "metric"
    }

    # Send the request
    response = requests.get(BASE_URL_CURRENT, params=params)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"API response for current weather: {data}")

        # Validate if the returned country matches the requested country
        if data["sys"]["country"] != request.country:
            raise ValueError(f"Mismatch in country: Expected {request.country}, but got {data['sys']['country']}.")

        # Return weather data
        return [WeatherData(
            city=data["name"],
            country=data["sys"]["country"],
            date=datetime.utcfromtimestamp(data["dt"]),
            temperature=data["main"]["temp"],
            weather_description=data["weather"][0]["description"]
        )]
    else:
        logging.error(f"Error fetching current weather: {response.status_code}, {response.text}")
        raise ValueError(f"Error fetching current weather: {response.status_code}, {response.text}")



def fetch_forecast_weather(request: WeatherRequest):
    """
    Fetch weather forecast data.
    """
    params = {
        "q": request.city if request.city else None,
        "zip": f"{request.postal_code},{request.country}" if request.postal_code else None,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL_FORECAST, params=params)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"API response for forecast weather: {data}")
        weather_data_list = []
        for entry in data["list"]:
            forecast_date = datetime.utcfromtimestamp(entry["dt"])
            weather_data_list.append(WeatherData(
                city=data["city"]["name"],
                country=data["city"]["country"],
                date=forecast_date,
                temperature=entry["main"]["temp"],
                weather_description=entry["weather"][0]["description"]
            ))
        return weather_data_list
    else:
        logging.error(f"Error fetching forecast weather: {response.status_code}, {response.text}")
        raise ValueError(f"Error fetching forecast weather: {response.status_code}, {response.text}")


def fetch_historical_weather(request: WeatherRequest):
    """
    Fetch historical weather data.
    """
    # Fetch coordinates for the city
    coordinates = get_coordinates(request.city, request.country)
    if not coordinates:
        raise ValueError(f"Could not fetch coordinates for city: {request.city}, country: {request.country}")

    lat, lon = coordinates["lat"], coordinates["lon"]
    weather_data_list = []
    current_date = request.start_date

    while current_date <= request.end_date:
        unix_timestamp = int(current_date.timestamp())
        params = {
            "lat": lat,
            "lon": lon,
            "dt": unix_timestamp,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL_HISTORICAL, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"API response for historical weather on {current_date}: {data}")
            weather_data_list.append(WeatherData(
                city=request.city,
                country=request.country,
                date=current_date,
                temperature=data["current"]["temp"],
                weather_description=data["current"]["weather"][0]["description"]
            ))
        else:
            logging.error(f"Error fetching historical weather: {response.status_code}, {response.text}")
            raise ValueError(f"Error fetching historical weather: {response.status_code}, {response.text}")
        current_date += timedelta(days=1)

    return weather_data_list


def get_coordinates(city: str, country: str):
    """
    Fetch geographical coordinates (latitude and longitude) for a given city and country.

    Parameters:
        city (str): Name of the city.
        country (str): ISO 3166-1 alpha-2 country code (e.g., 'PL').

    Returns:
        dict: A dictionary containing 'lat' and 'lon' if found, otherwise None.
    """
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{city},{country}",
        "limit": 1,
        "appid": API_KEY
    }

    response = requests.get(geo_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
        else:
            logging.error(f"Coordinates not found for city: {city}, country: {country}")
            return None
    else:
        logging.error(f"Error fetching coordinates: {response.status_code}, {response.text}")
        raise ValueError(f"Error fetching coordinates: {response.status_code}, {response.text}")
