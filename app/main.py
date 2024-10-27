# app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.endpoints import patients, login, patient_details, doctor, patient_summary, patient_visits, patient_symptoms
from app.utils.middleware import LoggingMiddleware, RequestIDMiddleware
from app.db.session import engine
from app.db.base import Base 

def init_db():
    """
    Initialize the database by creating all tables.

    This function imports all the models to force the creation of the tables.
    """
    from app.db import models  
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Request ID middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(login.router, prefix=settings.API_V1_STR)
app.include_router(patient_details.router, prefix=settings.API_V1_STR)
app.include_router(doctor.router, prefix=settings.API_V1_STR)
app.include_router(patient_symptoms.router, prefix=settings.API_V1_STR)
app.include_router(patient_visits.router, prefix=settings.API_V1_STR)
app.include_router(patient_summary.router, prefix=settings.API_V1_STR)

init_db()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application")
    uvicorn.run(app, host="0.0.0.0", port=8000)