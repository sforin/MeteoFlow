from sqlalchemy.orm import Session
import models
import  schemas

def create_meteo_data(db: Session, data: schemas.MeteoDataCreate):
    db_data = models.MeteoData(
        timestamp=data.timestamp,
        station_id=data.station_id,
        latitude=data.location.latitude,
        longitude=data.location.longitude,
        altitude=data.location.altitude,
        temperature=data.weather.temperature,
        humidity=data.weather.humidity,
        wind_speed=data.weather.wind_speed,
        pressure=data.weather.pressure,
        solar_radiation=data.weather.solar_radiation
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def get_all_meteo_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MeteoData).offset(skip).limit(limit).all()
