from state.database import Base, engine
from state.models import WeatherState

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✓ SQLite DB inizializzato.")
