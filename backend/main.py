from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from services.process_service import ProcessService
import schemas
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Consulta Processual API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Consulta Processual API"}

@app.get("/processes/{number}", response_model=schemas.ProcessResponse)
async def get_process(number: str, db: Session = Depends(get_db)):
    service = ProcessService(db)
    try:
        process = await service.get_or_update_process(number)
        if not process:
            raise HTTPException(status_code=404, detail="Processo não encontrado na base pública")
        return process
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to Consulta Processual API"}
