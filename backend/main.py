from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db
from .services.process_service import ProcessService
from .services.stats_service import StatsService
from .services.sql_integration_service import SQLIntegrationService
from . import schemas
from .config import settings
from .error_handlers import register_exception_handlers
from .exceptions import ProcessNotFoundException

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

@app.get("/stats", response_model=schemas.DatabaseStats)
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get statistics from the local database.
    Returns aggregated data about stored processes for BI/Analytics.
    """
    service = StatsService(db)
    return service.get_database_stats()

@app.get("/")
async def root():
    return {"message": "Welcome to Consulta Processual API"}

@app.post("/sql/test", response_model=schemas.SQLConnectionTestResponse)
async def test_sql_connection(config: schemas.SQLConnectionConfig):
    """
    Test an external SQL connection and return a sample of process numbers.
    """
    service = SQLIntegrationService(config)
    return service.test_connection()

@app.post("/sql/import", response_model=schemas.BulkProcessResponse)
async def import_from_sql(request: schemas.SQLImportRequest, db: Session = Depends(get_db)):
    """
    Fetch process numbers from external SQL and trigger bulk search/update.
    """
    sql_service = SQLIntegrationService(request)
    numbers = sql_service.get_process_numbers()
    
    if not numbers:
        return schemas.BulkProcessResponse(results=[], failures=["Nenhum processo encontrado na consulta SQL"])
        
    process_service = ProcessService(db)
    return await process_service.get_bulk_processes(numbers)

@app.get("/settings/ai", response_model=schemas.AISettingsResponse)
async def get_ai_settings():
    """Returns the current AI settings with a masked API key."""
    key = settings.OPENROUTER_API_KEY
    masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    return schemas.AISettingsResponse(
        success=True,
        message="Configurações recuperadas",
        masked_key=masked if key else "Não configurada"
    )

@app.post("/settings/ai", response_model=schemas.AISettingsResponse)
async def update_ai_settings(config: schemas.AISettingsUpdate):
    """Updates the AI API key and persists it to .env."""
    try:
        # Update in-memory settings
        settings.OPENROUTER_API_KEY = config.api_key
        settings.AI_MODEL = config.model or settings.AI_MODEL
        
        # Persist to .env
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        # Update or add OPENROUTER_API_KEY
        key_found = False
        model_found = False
        new_lines = []
        for line in lines:
            if line.startswith("OPENROUTER_API_KEY="):
                new_lines.append(f"OPENROUTER_API_KEY={config.api_key}\n")
                key_found = True
            elif line.startswith("AI_MODEL="):
                new_lines.append(f"AI_MODEL={config.model}\n")
                model_found = True
            else:
                new_lines.append(line)
        
        if not key_found:
            new_lines.append(f"OPENROUTER_API_KEY={config.api_key}\n")
        if not model_found and config.model:
            new_lines.append(f"AI_MODEL={config.model}\n")
            
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        masked = f"{config.api_key[:4]}...{config.api_key[-4:]}" if len(config.api_key) > 8 else "****"
        return schemas.AISettingsResponse(
            success=True,
            message="Configuração salva com sucesso no .env!",
            masked_key=masked
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
