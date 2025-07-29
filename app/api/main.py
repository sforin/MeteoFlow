import models
import database
import routes

from fastapi import FastAPI

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="MeteoFlow API")

app.include_router(routes.router, prefix="/api", tags=["Meteo"])

@app.get("/health")
def health_check():
    return {"status": "ok"}



