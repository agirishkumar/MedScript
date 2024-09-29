import os
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import engine, get_db, db_operation
from app import crud, schemas, models
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=100000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response

app = FastAPI(title="Medical Diagnostic Assistant API",
    description="API for AI-powered medical diagnostics",
    version="1.0.0",
    docs_url="/docs", 
    redoc_url="/redoc")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add Request ID middleware
app.add_middleware(RequestIDMiddleware)

# API versioning prefix
API_V1_STR = "/api/v1"

# Create database tables
models.Base.metadata.create_all(bind=engine)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"message": "Favicon not found"})


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Medical Diagnostic Assistant API"}

@app.get(f"{API_V1_STR}/health")
async def health_check(request: Request):
    logger.info(f"Health check endpoint accessed. Request ID: {request.state.request_id}")
    return {"status": "healthy", "request_id": request.state.request_id}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}. Request ID: {request.state.request_id}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "request_id": request.state.request_id},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unexpected error occurred: {str(exc)}. Request ID: {request.state.request_id}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred", "request_id": request.state.request_id},
    )

patient_tag = "patients"

@app.post(f"{API_V1_STR}/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_patient(db=db, patient=patient)
    except Exception as e:
        logger.error(f"Failed to create patient: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create patient")


@app.get(f"{API_V1_STR}/patients/", response_model=list[schemas.Patient], tags=[patient_tag])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_patients(db, skip=skip, limit=limit)

# Update other endpoints similarly

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)