from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from services.process_service import ProcessService
import schemas
from dotenv import load_dotenv
from config import settings
from error_handlers import register_exception_handlers
from exceptions import ProcessNotFoundException

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Register custom exception handlers
register_exception_handlers(app)

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Consulta Processual API"}

@app.get("/processes/{number}", response_model=schemas.ProcessResponse)
async def get_process(number: str, db: Session = Depends(get_db)):
    """
    Retrieve a single process by its CNJ number.
    Fetches from DataJud API and stores in local database.
    """
    service = ProcessService(db)
    process = await service.get_or_update_process(number)
    if not process:
        raise ProcessNotFoundException(number)
    return process


@app.post("/processes/bulk", response_model=schemas.BulkProcessResponse)
async def get_processes_bulk(
    request: schemas.BulkProcessRequest, db: Session = Depends(get_db)
):
    """
    Retrieve multiple processes by their CNJ numbers.
    Returns both successful results and failed process numbers.
    """
    service = ProcessService(db)
    return await service.get_bulk_processes(request.numbers)

@app.get("/")
async def root():
    return {"message": "Welcome to Consulta Processual API"}
