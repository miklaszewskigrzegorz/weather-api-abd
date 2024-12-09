##2024_12_08### abd ### wyzwanie_1 # app  # FastAPI
##gm##

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import init_db, SessionLocal
from models import WeatherRequest, WeatherResponse
from services import fetch_weather_data
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI application
app = FastAPI()

# Initialize the database
init_db()


# Dependency: Database session
def get_db():
    """
    Dependency to provide a database session.
    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/weather",
    response_model=List[WeatherResponse],
    summary="Fetch weather data",
    description="""
    Fetch weather data for a given city, postal code, or date range.

    Example Requests:
    - {"city": "Warsaw", "country": "PL", "postal_code": null, "request_type": "current"}
    - {"city": "Warsaw", "country": "PL", "postal_code": null, "start_date": "2024-12-01T00:00:00", "end_date": "2024-12-05T00:00:00", "request_type": "historical"}
    - {"city": "Warsaw", "country": "PL", "postal_code": null, "request_type": "forecast"}
    """
)
def get_weather(request: WeatherRequest, db: Session = Depends(get_db)):
    """
    Endpoint to fetch weather data.

    Parameters:
        request (WeatherRequest): Contains the city, country, postal code, and date range.
        db (Session): Database session for saving fetched data.

    Returns:
        List[WeatherResponse]: List of weather data objects for the requested type.
    """
    try:
        logging.info(f"Received request: {request}")

        # Fetch data from the appropriate API endpoint
        weather_data = fetch_weather_data(request)

        # Save weather data to the database
        for data in weather_data:
            db.add(data)
        db.commit()
        logging.info("Weather data saved to the database.")

        # Return the response
        return [
            WeatherResponse(
                city=data.city,
                country=data.country,
                date=data.date,
                temperature=data.temperature,
                weather_description=data.weather_description,
            )
            for data in weather_data
        ]

    except HTTPException as e:
        logging.error(f"HTTPException: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
