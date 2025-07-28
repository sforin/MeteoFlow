from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    latitude: float
    longitude: float
    altitude: float

class Weather(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    pressure: float
    solar_radiation: float

class MeteoDataCreate(BaseModel):
    timestamp: int
    station_id: str
    location: Location
    weather: Weather


class MeteoDataRead(MeteoDataCreate):
    id: int

    class Config:
        orm_mode = True
