import asyncio
import json
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
from sqlalchemy import text, func, distinct
from sqlalchemy.orm import Session
from .database import get_db, SessionLocal
from .services.process_service import ProcessService
from .services.stats_service import StatsService
from .services.sql_integration_service import SQLIntegrationService
from .services.metrics_service import get_metrics_service
from .services.bulk_queue import bulk_job_manager, run_bulk_job
from .services.dependency_container import get_fusion_service, get_fusion_api_client, update_fusion_cookie
from .services.fusion_service import FusionService
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

# Sentry setup (Story: REM-013)
SENTRY_AVAILABLE = False
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    pass

if SENTRY_AVAILABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )

# Initialize loggers (Story: REM-016 — Centralized Logging Local)
logger = setup_logger()
setup_access_logger()  # Initializes "access" logger used by RequestLoggerMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    models.Base.metadata.create_all(bind=engine)

    # Migrate: add phase and classification_log columns to search_history if missing
    from sqlalchemy import inspect as sa_inspect, text as sa_text
    inspector = sa_inspect(engine)
    existing_cols = {c["name"] for c in inspector.get_columns("search_history")}
    with engine.connect() as conn:
        if "phase" not in existing_cols:
            conn.execute(sa_text("ALTER TABLE search_history ADD COLUMN phase VARCHAR"))
            conn.commit()
        if "classification_log" not in existing_cols:
            conn.execute(sa_text("ALTER TABLE search_history ADD COLUMN classification_log TEXT"))
            conn.commit()

    # Migrate: ensure phase_corrections table exists
    inspector = sa_inspect(engine)
    existing_tables = {t.lower() for t in inspector.get_table_names()}
    if "phase_corrections" not in existing_tables:
        models.Base.metadata.tables["phase_corrections"].create(bind=engine)

    # Migrate: add hierarchical classification columns (stage, substage, transit_julgado)
    _hierarchical_cols = {
        "processes": ["stage", "substage", "transit_julgado"],
        "search_history": ["stage", "substage", "transit_julgado"],
        "phase_corrections": ["corrected_stage", "corrected_substage", "corrected_transit"],
        "phase_confirmations": ["confirmed_stage", "confirmed_substage", "confirmed_transit"],
    }
    inspector = sa_inspect(engine)
    with engine.connect() as conn:
        for table_name, cols in _hierarchical_cols.items():
            if table_name not in {t.lower() for t in inspector.get_table_names()}:
                continue
            existing = {c["name"] for c in inspector.get_columns(table_name)}
            for col in cols:
                if col not in existing:
                    col_type = "INTEGER" if col.endswith("stage") and not col.endswith("substage") else "VARCHAR"
                    conn.execute(sa_text(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}"))
            conn.commit()

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
    # Ensure JSON responses declare UTF-8 charset to prevent encoding issues (acentos, etc)
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type and "charset" not in content_type:
        response.headers["content-type"] = f"{content_type}; charset=utf-8"
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
async def get_process(
    number: str,
    request: Request,
    db: Session = Depends(get_db),
    fusion_service: FusionService = Depends(get_fusion_service),
):
    """
    Retrieve a single process by its CNJ number.
    Fetches from DataJud API and stores in local database.
    Falls back to Fusion/PAV if not found in DataJud.
    """
    service = ProcessService(db, fusion_service=fusion_service)
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
    request: Request,
    body: schemas.BulkProcessRequest,
    db: Session = Depends(get_db),
    fusion_service: FusionService = Depends(get_fusion_service),
):
    """
    Retrieve multiple processes by their CNJ numbers in parallel.
    Uses asyncio.gather() with configurable concurrency limit.
    Returns both successful results and failed process numbers.

    Story: PERF-ARCH-001 - Async Bulk Processing
    """
    service = ProcessService(db, fusion_service=fusion_service)
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
            fusion_service=get_fusion_service() if get_fusion_api_client() and get_fusion_api_client().session_cookie else None,
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


@app.get("/fusion/test", tags=["fusion"])
async def test_fusion_connection(numero_cnj: str) -> dict:
    """
    Testa a integração Fusion consultando um processo pelo número CNJ.
    Útil para verificar cookie de sessão e conectividade.

    Args:
        numero_cnj: número CNJ para testar (com ou sem formatação).
    """
    fusion_service = get_fusion_service()
    result = await fusion_service.get_document_tree(numero_cnj)

    if result is None:
        return {
            "success": False,
            "message": "Processo não encontrado no Fusion/PAV",
            "numero_cnj": numero_cnj,
        }

    return {
        "success": True,
        "message": f"Processo encontrado via {result.fonte}",
        "numero_cnj": numero_cnj,
        "fonte": result.fonte,
        "classe_processual": result.classe_processual,
        "sistema": result.sistema,
        "total_movimentos": len(result.movimentos),
        "neo_id": result.neo_id,
    }


@app.patch("/fusion/cookie", tags=["fusion"])
async def update_fusion_cookie_endpoint(payload: dict) -> dict:
    """
    Atualiza o cookie de sessão PAV em runtime sem reiniciar o servidor.
    Chamado pelo bookmarklet quando o usuário está logado no PAV.

    Body: {"cookie": "JSESSIONID=ABC123..."}
    """
    new_cookie = payload.get("cookie", "").strip()
    if not new_cookie:
        return {"success": False, "message": "Cookie não informado."}
    if "JSESSIONID" not in new_cookie:
        return {"success": False, "message": "Cookie inválido — deve conter JSESSIONID."}

    update_fusion_cookie(new_cookie)
    preview = new_cookie[-8:] if len(new_cookie) > 8 else new_cookie
    return {
        "success": True,
        "message": f"Cookie PAV atualizado (…{preview}).",
    }


@app.get("/fusion/status", tags=["fusion"])
async def fusion_session_status() -> dict:
    """
    Retorna o status atual da sessão PAV: se há cookie configurado e
    se a sessão está ativa (via check_session rápido).
    """
    api_client = get_fusion_api_client()
    if api_client is None or not api_client.session_cookie:
        return {
            "configured": False,
            "alive": False,
            "message": "Cookie PAV não configurado.",
        }

    alive, status_code = await api_client.check_session()
    cookie = api_client.session_cookie
    preview = "…" + cookie[-8:] if len(cookie) > 8 else cookie
    return {
        "configured": True,
        "alive": alive,
        "status_code": status_code,
        "cookie_preview": preview,
        "message": "Sessão PAV ativa." if alive else f"Sessão PAV expirada (HTTP {status_code}).",
    }


@app.get("/history", response_model=List[schemas.HistoryResponse])
async def get_search_history(db: Session = Depends(get_db)):
    """Retrieve the recent search history."""
    return db.query(models.SearchHistory).order_by(models.SearchHistory.created_at.desc()).all()

@app.delete("/history")
async def clear_search_history(db: Session = Depends(get_db)):
    """Clear all search history."""
    db.query(models.SearchHistory).delete(synchronize_session=False)
    db.query(models.PhaseCorrection).delete(synchronize_session=False)
    db.query(models.PhaseConfirmation).delete(synchronize_session=False)
    db.commit()
    return {"message": "Histórico limpo"}


@app.delete("/stats", tags=["processes"])
async def clear_stats(db: Session = Depends(get_db)):
    """Remove todos os processos e movimentos armazenados localmente."""
    db.query(models.Movement).delete(synchronize_session=False)
    db.query(models.Process).delete(synchronize_session=False)
    db.query(models.PhaseCorrection).delete(synchronize_session=False)
    db.query(models.PhaseConfirmation).delete(synchronize_session=False)
    db.commit()
    return {"message": "Estatísticas resetadas"}


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


@app.post("/processes/{number}/phase-correction", response_model=schemas.PhaseCorrectionResponse, tags=["processes"])
@limiter.limit("60/minute")
async def submit_phase_correction(
    number: str,
    request: Request,
    correction: schemas.PhaseCorrectionCreate,
    db: Session = Depends(get_db),
):
    """
    Submeter uma correção de fase processual.
    Registra o par (fase_original, fase_corrigida, motivo) para retreinamento do ML.

    Story: Edição Manual de Fase Processual
    """
    from .constants import VALID_PHASE_CODES

    # Validar código de fase
    corrected_phase = correction.corrected_phase.zfill(2)
    if corrected_phase not in VALID_PHASE_CODES:
        raise HTTPException(
            status_code=400,
            detail=f"Código de fase inválido. Use 01-15."
        )

    # Registrar correção
    phase_correction = models.PhaseCorrection(
        process_number=number,
        original_phase=correction.original_phase,
        corrected_phase=corrected_phase,
        reason=correction.reason,
        source_tab=correction.source_tab,
        classification_log_snapshot=(
            json.dumps(correction.classification_log_snapshot, ensure_ascii=False)
            if correction.classification_log_snapshot is not None else None
        ),
    )
    db.add(phase_correction)
    db.commit()
    db.refresh(phase_correction)

    return phase_correction


@app.get("/phase-corrections/analytics", tags=["processes"])
@limiter.limit("60/minute")
async def get_phase_corrections_analytics(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Retorna estatísticas de correções de classificação de fase.

    Métricas retornadas:
    - total_consultados: total de processos consultados no histórico
    - total_corrigidos: total de processos com pelo menos uma correção
    - total_sem_correcao: total_consultados - total_corrigidos (processos sem erro)
    - taxa_acerto_pct: percentual de processos sem correção (acerto do classificador)
    - correcoes_por_fase_original: fases que geraram mais erros, ordenadas por frequência
    - correcoes_por_fase_corrigida: para quais fases os erros foram corrigidos
    """
    total_consultados = db.query(func.count(models.SearchHistory.id)).scalar()
    total_corrigidos = db.query(func.count(distinct(models.PhaseCorrection.process_number))).scalar()
    total_sem_correcao = max(0, total_consultados - total_corrigidos)
    taxa_acerto = (
        round((total_sem_correcao / total_consultados) * 100, 1)
        if total_consultados > 0
        else 0.0
    )

    por_fase_original = (
        db.query(
            models.PhaseCorrection.original_phase,
            func.count(models.PhaseCorrection.id).label("total"),
        )
        .group_by(models.PhaseCorrection.original_phase)
        .order_by(func.count(models.PhaseCorrection.id).desc())
        .all()
    )

    por_fase_corrigida = (
        db.query(
            models.PhaseCorrection.corrected_phase,
            func.count(models.PhaseCorrection.id).label("total"),
        )
        .group_by(models.PhaseCorrection.corrected_phase)
        .order_by(models.PhaseCorrection.corrected_phase)
        .all()
    )

    total_confirmados = db.query(func.count(models.PhaseConfirmation.id)).scalar()

    return {
        "total_consultados": total_consultados,
        "total_corrigidos": total_corrigidos,
        "total_sem_correcao": total_sem_correcao,
        "taxa_acerto_pct": taxa_acerto,
        "total_confirmados": total_confirmados,
        "correcoes_por_fase_original": [
            {"fase": r.original_phase or "Indefinido", "total": r.total}
            for r in por_fase_original
        ],
        "correcoes_por_fase_corrigida": [
            {"fase": r.corrected_phase, "total": r.total}
            for r in por_fase_corrigida
        ],
    }


@app.get("/phase-corrections/latest", tags=["processes"])
@limiter.limit("100/minute")
async def get_latest_phase_corrections(
    request: Request,
    db: Session = Depends(get_db),
):
    """Retorna a correção mais recente por processo (mapa process_number → corrected_phase)."""
    subq = (
        db.query(
            models.PhaseCorrection.process_number,
            func.max(models.PhaseCorrection.id).label("max_id"),
        )
        .group_by(models.PhaseCorrection.process_number)
        .subquery()
    )
    rows = (
        db.query(models.PhaseCorrection.process_number, models.PhaseCorrection.corrected_phase)
        .join(subq, models.PhaseCorrection.id == subq.c.max_id)
        .all()
    )
    return {"corrections": {r.process_number: r.corrected_phase for r in rows}}


@app.get("/phase-confirmations", tags=["processes"])
@limiter.limit("100/minute")
async def list_confirmed_processes(
    request: Request,
    db: Session = Depends(get_db),
):
    """Retorna lista de process_numbers que foram confirmados como corretos."""
    confirmed = db.query(models.PhaseConfirmation.process_number).all()
    return {"confirmed_processes": [r[0] for r in confirmed]}


@app.post("/phase-confirmations", tags=["processes"])
@limiter.limit("60/minute")
async def confirm_phase(
    request: Request,
    body: dict,
    db: Session = Depends(get_db),
):
    """Registra que a classificação de fase está correta (sem necessidade de correção)."""
    existing = db.query(models.PhaseConfirmation).filter_by(
        process_number=body["process_number"]
    ).first()
    if existing:
        existing.confirmed_phase = body["confirmed_phase"]
        db.commit()
        return {"message": "updated"}
    db.add(models.PhaseConfirmation(
        process_number=body["process_number"],
        confirmed_phase=body["confirmed_phase"],
    ))
    db.commit()
    return {"message": "confirmed"}


@app.get("/phase-corrections", response_model=List[schemas.PhaseCorrectionResponse], tags=["processes"])
@limiter.limit("100/minute")
async def list_phase_corrections(
    request: Request,
    process_number: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Listar correções de fase.

    Query params:
    - process_number: filtrar por número do processo
    - limit: máximo 1000 (padrão: 100)
    - offset: paginação (padrão: 0)
    """
    limit = min(limit, 1000)
    query = db.query(models.PhaseCorrection)

    if process_number:
        query = query.filter(models.PhaseCorrection.process_number == process_number)

    corrections = query.order_by(models.PhaseCorrection.created_at.desc()).offset(offset).limit(limit).all()
    return corrections


@app.get("/circuit-breaker/status", tags=["health"])
async def get_circuit_breaker_status():
    """Get status of all registered circuit breakers."""
    from .patterns.circuit_breaker import get_registry
    return get_registry().get_status()
