import asyncio
import os
import logging

from dotenv import load_dotenv
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import get_db, SessionLocal
from .services.process_service import ProcessService
from .services.stats_service import StatsService
from .services.sql_integration_service import SQLIntegrationService
from .services.metrics_service import get_metrics_service
from .services.bulk_queue import bulk_job_manager, run_bulk_job
from . import schemas
from .config import settings
from .error_handlers import register_exception_handlers
from .exceptions import ProcessNotFoundException
from . import models
from .database import engine
from .utils.logger import setup_logger, setup_access_logger
from .utils.redact import redact_dict
from .middleware import CorrelationIdMiddleware, RequestLoggerMiddleware
from contextlib import asynccontextmanager

# Initialize loggers (Story: REM-016 — Centralized Logging Local)
logger = setup_logger()
setup_access_logger()  # Initializes "access" logger used by RequestLoggerMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    models.Base.metadata.create_all(bind=engine)
    yield

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for querying and analyzing judicial processes from DataJud (Conselho Nacional de Justiça).",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and readiness endpoints",
        },
        {
            "name": "processes",
            "description": "Query and retrieve legal process information",
        },
        {
            "name": "metrics",
            "description": "Performance metrics and monitoring",
        },
        {
            "name": "stats",
            "description": "Database statistics and analytics",
        },
        {
            "name": "history",
            "description": "Search history management",
        },
    ],
)

# Initialize rate limiter (Story: REM-004 DB-002)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register custom exception handlers
register_exception_handlers(app)


# Global exception handler for logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions and return error response."""
    logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Observability middlewares — Story: REM-016 (Centralized Logging Local)
# Order matters: CorrelationId must run before RequestLogger so the ID is available.
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware — Story: REM-051 (XSS Vulnerability Audit)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://plausible.io; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' https://plausible.io; "
        "font-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response

@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring tools and load balancers.
    Verifies database connectivity and API readiness.

    Story: DEPLOY-ARCH-004 - Health Checks
    """
    try:
        # Verify database connectivity
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "Consulta Processual API",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            content={"status": "unhealthy", "error": "Database connection failed"},
            status_code=503
        )


@app.get("/ready", tags=["health"])
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe for Kubernetes and container orchestration.
    Indicates if service is ready to accept traffic.

    Story: DEPLOY-ARCH-004 - Health Checks
    """
    try:
        # Verify database connectivity
        db.execute(text("SELECT 1"))
        return {"ready": True, "version": settings.VERSION}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            content={"ready": False, "error": str(e)},
            status_code=503
        )


@app.post("/api/logs")
async def receive_logs(logs: List[dict]):
    """Receive frontend logs and write to backend log file."""
    for log in logs:
        logger.info(
            log.get('message', 'Frontend log'),
            extra={
                'service': 'frontend',
                'level': log.get('level'),
            }
        )
    return {"received": len(logs)}

@app.get("/processes/{number}", response_model=schemas.ProcessResponse)
@limiter.limit("100/minute")
async def get_process(number: str, request: Request, db: Session = Depends(get_db)):
    """
    Retrieve a single process by its CNJ number.
    Fetches from DataJud API and stores in local database.
    """
    service = ProcessService(db)
    process = await service.get_or_update_process(number)
    if not process:
        raise ProcessNotFoundException(number)
    return process


@app.get("/processes/{number}/instances")
async def get_process_instances(number: str, db: Session = Depends(get_db)):
    """
    Lista todas as instâncias de um processo (1ª, 2ª, Superiores).
    Retorna metadados sobre cada instância encontrada no DataJud.
    """
    service = ProcessService(db)
    return await service.get_all_instances(number)

@app.get("/processes/{number}/instances/{index}", response_model=schemas.ProcessResponse)
async def get_process_instance_detail(number: str, index: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific instance of a process from the stored raw data.
    """
    service = ProcessService(db)
    return await service.get_process_instance(number, index)


@app.post("/processes/bulk", response_model=schemas.BulkProcessResponse)
@limiter.limit("50/minute")
async def get_processes_bulk(
    request: Request, body: schemas.BulkProcessRequest, db: Session = Depends(get_db)
):
    """
    Retrieve multiple processes by their CNJ numbers in parallel.
    Uses asyncio.gather() with configurable concurrency limit.
    Returns both successful results and failed process numbers.

    Story: PERF-ARCH-001 - Async Bulk Processing
    """
    service = ProcessService(db)
    return await service.get_bulk_processes(
        body.numbers,
        max_concurrent=settings.BULK_MAX_CONCURRENT
    )

@app.post("/processes/bulk/submit", response_model=schemas.BulkJobStatusResponse)
@limiter.limit("20/minute")
async def submit_bulk_job(
    request: Request, body: schemas.BulkSubmitRequest
):
    """
    Submit a bulk processing job and return a job_id immediately.

    The job processes all numbers in the background using asyncio with a
    configurable concurrency limit. Poll GET /processes/bulk/{job_id} for
    progress and results. Supports thousands of numbers without HTTP timeout.
    """
    job = await bulk_job_manager.create(body.numbers)
    # Fire-and-forget: passes SessionLocal factory so the background task
    # creates its own session (the request session closes when handler returns).
    asyncio.create_task(
        run_bulk_job(
            job=job,
            numbers=body.numbers,
            db_factory=SessionLocal,
            max_concurrent=settings.BULK_MAX_CONCURRENT,
            request_delay=settings.BULK_REQUEST_DELAY,
        )
    )
    return schemas.BulkJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        total=job.total,
        processed=job.processed,
        results_count=job.results_count,
        failures_count=job.failures_count,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@app.get("/processes/bulk/{job_id}", response_model=schemas.BulkJobResultsResponse)
async def get_bulk_job(
    job_id: str,
    page: int = 1,
    per_page: int = 50,
):
    """
    Poll bulk job status and retrieve paginated results.

    - While status is 'running': returns progress counters + partial results.
    - When status is 'done': returns all results (paginated).
    - per_page max: 200.
    """
    per_page = min(per_page, 200)
    job = await bulk_job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado ou expirado.")

    total_pages = max(1, -(-job.results_count // per_page))  # ceiling division
    results_page = job.get_results_page(page, per_page)

    return schemas.BulkJobResultsResponse(
        job_id=job.job_id,
        status=job.status,
        total=job.total,
        processed=job.processed,
        failures=job.failures,
        results=results_page,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


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
    Uses async parallel processing with configurable concurrency.
    """
    sql_service = SQLIntegrationService(request)
    numbers = sql_service.get_process_numbers()

    if not numbers:
        return schemas.BulkProcessResponse(results=[], failures=["Nenhum processo encontrado na consulta SQL"])

    process_service = ProcessService(db)
    return await process_service.get_bulk_processes(
        numbers,
        max_concurrent=settings.BULK_MAX_CONCURRENT
    )


@app.get("/history", response_model=List[schemas.HistoryResponse])
async def get_search_history(db: Session = Depends(get_db)):
    """Retrieve the recent search history."""
    return db.query(models.SearchHistory).order_by(models.SearchHistory.created_at.desc()).limit(50).all()

@app.delete("/history")
async def clear_search_history(db: Session = Depends(get_db)):
    """Clear all search history."""
    db.query(models.SearchHistory).delete()
    db.commit()
    return {"message": "Histórico limpo"}


@app.get("/metrics", response_model=schemas.MetricsResponse, tags=["metrics"])
async def get_metrics(hours: int = 24):
    """Get current performance metrics and historical data."""
    metrics_service = get_metrics_service()
    current = metrics_service.get_current_metrics()
    history = metrics_service.get_history(hours=hours)
    alerts = metrics_service.get_alerts()

    return schemas.MetricsResponse(
        current=current,
        history=history,
        alerts=alerts
    )


@app.get("/metrics/alerts", response_model=List[schemas.AlertResponse], tags=["metrics"])
async def get_alerts(limit: int = 20):
    """Get recent performance alerts."""
    metrics_service = get_metrics_service()
    return metrics_service.get_alerts(limit=limit)


@app.get("/circuit-breaker/status", tags=["health"])
async def get_circuit_breaker_status():
    """Get status of all registered circuit breakers."""
    from .patterns.circuit_breaker import get_registry
    return get_registry().get_status()
