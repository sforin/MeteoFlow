from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
import crud
from database import SessionLocal, get_db
from schemas import MeteoDataCreate

router = APIRouter()

@router.post("/meteo/", response_model=schemas.MeteoDataRead)
def create_data(data: schemas.MeteoDataCreate, db: Session = Depends(get_db)):
    return crud.create_meteo_data(db, data)

@router.get("/meteo/", response_model=list[schemas.MeteoDataRead])
def read_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_meteo_data(db, skip=skip, limit=limit)

@router.post("/meteo", response_model=MeteoDataCreate)
def create_data(data: MeteoDataCreate, db: Session = Depends(get_db)):
    saved = crud.create_meteo_data(db, data)
    return {
        "timestamp": saved.timestamp,
        "station_id": saved.station_id,
        "location": {
            "latitude": saved.latitude,
            "longitude": saved.longitude,
            "altitude": saved.altitude
        },
        "weather": {
            "temperature": saved.temperature,
            "humidity": saved.humidity,
            "wind_speed": saved.wind_speed,
            "pressure": saved.pressure,
            "solar_radiation": saved.solar_radiation
        }
    }