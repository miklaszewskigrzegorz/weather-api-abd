from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WeatherRequest(BaseModel):
    """
    Model representing the input parameters for fetching weather data.

    Attributes:
        city (Optional[str]): Name of the city (nullable).
        country (Optional[str]): Country code in ISO 3166-1 alpha-2 format (nullable).
        postal_code (Optional[str]): Postal code for location-based weather retrieval (nullable).
        start_date (Optional[datetime]): Start date for weather data (nullable).
        end_date (Optional[datetime]): End date for weather data (nullable).
        request_type (Optional[str]): Type of weather data ("current", "historical", "forecast").
    """
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    request_type: Optional[str] = "current"  # Default to current weather


class WeatherResponse(BaseModel):
    """
    Model representing the response for weather data.

    Attributes:
        city (str): Name of the city.
        country (str): Country code in ISO 3166-1 alpha-2 format.
        date (datetime): Date of the weather data.
        temperature (float): Temperature in Celsius.
        weather_description (str): Description of the weather (e.g., 'clear sky').
    """
    city: str  # Name of the city
    country: str  # Country code (e.g., 'PL')
    date: datetime  # Date of the weather data
    temperature: float  # Temperature in Celsius
    weather_description: str  # Description of the weather (e.g., 'clear sky')
