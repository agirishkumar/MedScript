# app/main.py

'''
FastAPI application setup with middleware for logging, request ID, CORS, and routing for various endpoints.
'''

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.endpoints import patients, login, patient_details, doctor, patient_summary, patient_visits, patient_symptoms
from app.utils.middleware import LoggingMiddleware, RequestIDMiddleware
import app.db.base as db_base

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

db_base.init()

@app.get("/health", status_code=200)
def default():
    return {"message": "Server is up!"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application")
    uvicorn.run(app, host="0.0.0.0", port=8000)