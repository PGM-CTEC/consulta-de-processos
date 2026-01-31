from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

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
