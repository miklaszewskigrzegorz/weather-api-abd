from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Database connection URL
DATABASE_URL = "sqlite:///./weather.db"

# SQLAlchemy Base for defining ORM models
Base = declarative_base()

# Database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class WeatherData(Base):
    """
    SQLAlchemy ORM model for the weather_data table.

    Attributes:
        id (int): Primary key, unique identifier for each record.
        city (str): Name of the city.
        country (str): ISO 3166-1 alpha-2 country code (e.g., 'PL').
        date (datetime): The date for the weather data. Defaults to the current UTC time.
        temperature (float): The recorded temperature in Celsius.
        weather_description (str): A textual description of the weather (e.g., 'clear sky').
    """
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)  # Index for faster querying by city
    country = Column(String)  # Country code (e.g., 'PL')
    date = Column(DateTime, default=datetime.datetime.utcnow)  # Defaults to current UTC time
    temperature = Column(Float)  # Temperature in Celsius
    weather_description = Column(String)  # Description of the weather (e.g., 'clear sky')


def init_db():
    """
    Initializes the database by creating all tables defined in the ORM models.
    This function should be called during the application startup to ensure
    that the database schema is created before any operations.
    """
    Base.metadata.create_all(bind=engine)
