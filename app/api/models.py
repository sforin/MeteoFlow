from sqlalchemy import Column, Integer, String, Float, BigInteger
from database import Base

class MeteoData(Base):
    __tablename__ = "meteo_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(BigInteger)
    station_id = Column(String, index=True)

    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)

    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)
    solar_radiation = Column(Float)
