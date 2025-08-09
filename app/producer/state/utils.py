from state.models import WeatherState
from state.database import SessionLocal

WINDOW_SIZE = 10

def save_new_entry(entry_dict):
    session = SessionLocal()
    try:
        # Salva nuovo dato
        state = WeatherState(**entry_dict)
        session.add(state)
        session.commit()

        # Mantieni solo gli ultimi N per station_id
        recent = session.query(WeatherState)\
            .filter(WeatherState.station_id == entry_dict["station_id"])\
            .order_by(WeatherState.timestamp.desc())\
            .limit(WINDOW_SIZE).all()

        # Cancella gli altri
        ids_to_keep = [r.id for r in recent]
        session.query(WeatherState)\
            .filter(WeatherState.station_id == entry_dict["station_id"])\
            .filter(~WeatherState.id.in_(ids_to_keep)).delete(synchronize_session=False)

        session.commit()
    finally:
        session.close()

def get_recent_data(station_id):
    session = SessionLocal()
    try:
        return session.query(WeatherState)\
            .filter(WeatherState.station_id == station_id)\
            .order_by(WeatherState.timestamp.desc())\
            .limit(WINDOW_SIZE).all()
    finally:
        session.close()

