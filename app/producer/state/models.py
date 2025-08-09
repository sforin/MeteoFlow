from .database import Base
from sqlalchemy import Column, Integer, Float, String, BigInteger

class WeatherState(Base):
    __tablename__ = "weather_state"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, index=True)
    timestamp = Column(BigInteger)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)
    solar_radiation = Column(Float)
