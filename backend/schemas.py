from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Any
from datetime import datetime
from validators import ProcessNumberValidator
from exceptions import ValidationException

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

class ProcessCreate(ProcessBase):
    raw_data: Optional[Any] = None
    movements: List[MovementCreate] = []

class ProcessResponse(ProcessBase):
    id: int
    last_update: datetime
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
