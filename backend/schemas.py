from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Any
from datetime import datetime
from .validators import ProcessNumberValidator
from .exceptions import ValidationException

class MovementBase(BaseModel):
    date: datetime
    description: str
    code: Optional[str] = None

class MovementCreate(MovementBase):
    pass

class MovementResponse(MovementBase):
    id: int
    
    class Config:
        from_attributes = True

class ProcessBase(BaseModel):
    number: str
    class_nature: Optional[str] = None
    subject: Optional[str] = None
    court: Optional[str] = None
    tribunal_name: Optional[str] = None
    court_unit: Optional[str] = None
    district: Optional[str] = None
    judge: Optional[str] = None
    distribution_date: Optional[datetime] = None
    phase: Optional[str] = None
    phase_warning: Optional[str] = None

class HistoryResponse(BaseModel):
    id: int
    number: str
    court: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProcessCreate(ProcessBase):
    raw_data: Optional[Any] = None
    movements: List[MovementCreate] = []

class ProcessResponse(ProcessBase):
    id: int
    last_update: datetime
    raw_data: Optional[Any] = None
    movements: List[MovementResponse] = []

    class Config:
        from_attributes = True

class BulkProcessRequest(BaseModel):
    numbers: List[str] = Field(..., min_length=1, max_length=1000, description="List of process numbers (max 1000)")

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v):
        """Validate that we have a reasonable number of processes."""
        if not v:
            raise ValidationException("Lista de números não pode estar vazia")
        if len(v) > 1000:
            raise ValidationException("Máximo de 1000 processos por requisição")
        return v

class BulkProcessResponse(BaseModel):
    results: List[ProcessResponse]
    failures: List[str] = []

# --- Bulk Queue (async job) schemas ---

class BulkSubmitRequest(BaseModel):
    """Submit a bulk job — no upper limit on list size."""
    numbers: List[str] = Field(..., min_length=1, description="Números CNJ dos processos")

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v):
        if not v:
            raise ValidationException("Lista de números não pode estar vazia")
        # Sanitise whitespace and filter empty strings
        cleaned = [n.strip() for n in v if n and n.strip()]
        if not cleaned:
            raise ValidationException("Nenhum número de processo válido na lista")
        return cleaned

class BulkJobStatusResponse(BaseModel):
    """Lightweight status response — safe to poll every 2 s."""
    job_id: str
    status: str          # pending | running | done | error
    total: int
    processed: int
    results_count: int
    failures_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ProcessBulkResult(BaseModel):
    """Schema leve para resultados de busca em lote — omite raw_data e movements."""
    id: int
    number: str
    tribunal_name: Optional[str] = None
    court: Optional[str] = None
    court_unit: Optional[str] = None
    phase: Optional[str] = None
    phase_warning: Optional[str] = None
    class_nature: Optional[str] = None
    last_update: Optional[datetime] = None

    class Config:
        from_attributes = True

class BulkJobResultsResponse(BaseModel):
    """Full results response with pagination."""
    job_id: str
    status: str
    total: int
    processed: int
    failures: List[str]
    results: List[ProcessBulkResult]
    page: int
    per_page: int
    total_pages: int

class TribunalStats(BaseModel):
    tribunal_name: str
    count: int

class PhaseStats(BaseModel):
    phase: str
    count: int

class TimelineStats(BaseModel):
    month: str
    count: int

class DatabaseStats(BaseModel):
    total_processes: int
    total_movements: int
    tribunals: List[TribunalStats]
    phases: List[PhaseStats]
    timeline: List[TimelineStats]
    last_updated: Optional[datetime] = None

class SQLConnectionConfig(BaseModel):
    driver: str = Field(..., description="SQLAlchemy driver (ex: postgresql, mysql, mssql+pyodbc)")
    host: str
    port: int
    user: str
    password: str
    database: str
    query: str = Field(..., description="Query SQL para selecionar os números dos processos")

class SQLConnectionTestResponse(BaseModel):
    success: bool
    message: str
    sample_data: Optional[List[str]] = None

class SQLImportRequest(SQLConnectionConfig):
    pass


class MetricSnapshotResponse(BaseModel):
    """Current performance metrics snapshot."""
    timestamp: datetime
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput: float
    error_rate: float
    db_query_time: float
    cache_hit_ratio: float


class MetricsResponse(BaseModel):
    """Performance metrics response."""
    current: Optional[MetricSnapshotResponse] = None
    history: List[MetricSnapshotResponse] = []
    alerts: List[dict] = []


class AlertResponse(BaseModel):
    """Performance alert."""
    type: str
    message: str
    severity: str
    timestamp: str
