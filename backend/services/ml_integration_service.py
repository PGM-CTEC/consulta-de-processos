"""
Serviço de integração com modelos de Machine Learning.

Fornece interface unificada para treinar, avaliar e usar modelos
de classificação automática de fases processuais.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import httpx
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """Resultado de uma predição do modelo ML."""
    process_number: str
    predicted_phase: str
    confidence: float
    model_version: str
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            "process_number": self.process_number,
            "predicted_phase": self.predicted_phase,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TrainingJob:
    """Job de treinamento de modelo."""
    job_id: str
    status: str  # pending, training, completed, failed
    model_version: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_samples: int = 0
    accuracy: float = 0.0
    error: Optional[str] = None


class MLIntegrationService:
    """
    Gerencia integração com modelos de classificação automática de fases.

    Suporta múltiplos backends:
    - Local: Scikit-learn/FastText (em desenvolvimento)
    - Remote: API externa de ML
    - Hugging Face: Modelos pré-treinados
    """

    def __init__(
        self,
        backend: str = "local",
        model_path: Optional[Path] = None,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.backend = backend
        self.model_path = model_path or Path("./models")
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.current_model_version = "1.0.0"
        self.training_jobs: Dict[str, TrainingJob] = {}

        logger.info(f"ML Integration Service initialized with backend: {backend}")

    async def train_model(
        self,
        corrections_jsonl_path: str,
        model_name: str = "phase-classifier-v1"
    ) -> Tuple[bool, TrainingJob]:
        """
        Treina um novo modelo usando dados de correções.

        Args:
            corrections_jsonl_path: Caminho para arquivo JSONL com correções
            model_name: Nome do modelo a treinar

        Returns:
            (sucesso, training_job)
        """
        job_id = f"{model_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        job = TrainingJob(
            job_id=job_id,
            status="pending",
            model_version=self.current_model_version,
            created_at=datetime.now(),
            total_samples=0
        )

        self.training_jobs[job_id] = job

        try:
            if self.backend == "local":
                success = await self._train_local(corrections_jsonl_path, job)
            elif self.backend == "remote":
                success = await self._train_remote(corrections_jsonl_path, job)
            elif self.backend == "huggingface":
                success = await self._train_huggingface(corrections_jsonl_path, job)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

            if success:
                self.current_model_version = self._increment_version(self.current_model_version)
                job.status = "completed"
            else:
                job.status = "failed"

            return success, job

        except Exception as e:
            logger.error(f"Training failed for job {job_id}: {str(e)}")
            job.status = "failed"
            job.error = str(e)
            return False, job

    async def predict(
        self,
        process_number: str,
        original_phase: str,
        movements: Optional[List[Dict]] = None
    ) -> Optional[MLPrediction]:
        """
        Faz predição de fase usando o modelo treinado.

        Args:
            process_number: Número do processo
            original_phase: Fase atual do processo
            movements: Movimentos do processo (opcional)

        Returns:
            MLPrediction ou None se falhar
        """
        try:
            if self.backend == "local":
                prediction = await self._predict_local(process_number, original_phase, movements)
            elif self.backend == "remote":
                prediction = await self._predict_remote(process_number, original_phase, movements)
            elif self.backend == "huggingface":
                prediction = await self._predict_huggingface(process_number, original_phase, movements)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

            return prediction

        except Exception as e:
            logger.error(f"Prediction failed for process {process_number}: {str(e)}")
            return None

    async def evaluate_model(
        self,
        test_data_path: str
    ) -> Dict:
        """
        Avalia modelo usando dados de teste.

        Returns:
            Métricas de avaliação (accuracy, precision, recall, F1)
        """
        try:
            if self.backend == "local":
                metrics = await self._evaluate_local(test_data_path)
            elif self.backend == "remote":
                metrics = await self._evaluate_remote(test_data_path)
            elif self.backend == "huggingface":
                metrics = await self._evaluate_huggingface(test_data_path)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

            return metrics

        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return {"error": str(e)}

    # --- Backend-specific implementations ---

    async def _train_local(self, jsonl_path: str, job: TrainingJob) -> bool:
        """Treina modelo localmente usando scikit-learn."""
        job.status = "training"
        logger.info(f"Starting local training job {job.job_id}")

        # TODO: Implementar treinamento com scikit-learn
        # 1. Carregar dados JSONL
        # 2. Extrair features (one-hot encoding para fases, TF-IDF para razões)
        # 3. Treinar SVM ou RandomForest
        # 4. Salvar modelo com joblib

        await asyncio.sleep(1)  # Simulação
        job.total_samples = 100
        job.accuracy = 0.85
        job.completed_at = datetime.now()
        return True

    async def _predict_local(
        self,
        process_number: str,
        original_phase: str,
        movements: Optional[List[Dict]] = None
    ) -> Optional[MLPrediction]:
        """Faz predição usando modelo local."""
        # TODO: Implementar predição
        # 1. Carregar modelo salvo
        # 2. Extrair features do processo
        # 3. Fazer predição
        # 4. Retornar resultado com confidence

        # Mock para demonstração
        return MLPrediction(
            process_number=process_number,
            predicted_phase="05",
            confidence=0.87,
            model_version=self.current_model_version,
            timestamp=datetime.now()
        )

    async def _evaluate_local(self, test_data_path: str) -> Dict:
        """Avalia modelo localmente."""
        # TODO: Implementar avaliação
        return {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88,
            "f1": 0.85,
            "samples": 100
        }

    async def _train_remote(self, jsonl_path: str, job: TrainingJob) -> bool:
        """Treina modelo via API remota."""
        if not self.api_endpoint or not self.api_key:
            raise ValueError("API endpoint and key required for remote training")

        job.status = "training"
        logger.info(f"Submitting training job {job.job_id} to remote API")

        async with httpx.AsyncClient() as client:
            with open(jsonl_path, 'rb') as f:
                files = {'file': f}
                headers = {"Authorization": f"Bearer {self.api_key}"}

                response = await client.post(
                    f"{self.api_endpoint}/train",
                    files=files,
                    headers=headers,
                    timeout=300
                )

                if response.status_code == 200:
                    result = response.json()
                    job.total_samples = result.get("samples", 0)
                    job.accuracy = result.get("accuracy", 0.0)
                    job.completed_at = datetime.now()
                    return True

                return False

    async def _predict_remote(
        self,
        process_number: str,
        original_phase: str,
        movements: Optional[List[Dict]] = None
    ) -> Optional[MLPrediction]:
        """Faz predição via API remota."""
        if not self.api_endpoint or not self.api_key:
            raise ValueError("API endpoint and key required for remote prediction")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "process_number": process_number,
            "original_phase": original_phase,
            "movements": movements or []
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_endpoint}/predict",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return MLPrediction(
                    process_number=process_number,
                    predicted_phase=result["predicted_phase"],
                    confidence=result["confidence"],
                    model_version=result.get("model_version", self.current_model_version),
                    timestamp=datetime.now()
                )

            return None

    async def _evaluate_remote(self, test_data_path: str) -> Dict:
        """Avalia modelo via API remota."""
        if not self.api_endpoint or not self.api_key:
            raise ValueError("API endpoint and key required for remote evaluation")

        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            with open(test_data_path, 'rb') as f:
                files = {'file': f}
                response = await client.post(
                    f"{self.api_endpoint}/evaluate",
                    files=files,
                    headers=headers,
                    timeout=300
                )

                if response.status_code == 200:
                    return response.json()

                return {"error": "Evaluation failed"}

    async def _train_huggingface(self, jsonl_path: str, job: TrainingJob) -> bool:
        """Treina modelo via Hugging Face."""
        job.status = "training"
        logger.info(f"Submitting training job {job.job_id} to Hugging Face Hub")

        # TODO: Implementar fine-tuning em Hugging Face
        # Usar transformers library com DistilBERT ou similar
        await asyncio.sleep(1)
        job.total_samples = 100
        job.accuracy = 0.89
        job.completed_at = datetime.now()
        return True

    async def _predict_huggingface(
        self,
        process_number: str,
        original_phase: str,
        movements: Optional[List[Dict]] = None
    ) -> Optional[MLPrediction]:
        """Faz predição usando modelo Hugging Face."""
        # TODO: Implementar predição com transformers
        return MLPrediction(
            process_number=process_number,
            predicted_phase="05",
            confidence=0.91,
            model_version=self.current_model_version,
            timestamp=datetime.now()
        )

    async def _evaluate_huggingface(self, test_data_path: str) -> Dict:
        """Avalia modelo Hugging Face."""
        # TODO: Implementar avaliação
        return {
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.91,
            "f1": 0.89,
            "samples": 100
        }

    # --- Utilities ---

    @staticmethod
    def _increment_version(version: str) -> str:
        """Incrementa versão semântica (patch)."""
        parts = version.split('.')
        parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)

    def get_training_job(self, job_id: str) -> Optional[TrainingJob]:
        """Obtém status de um job de treinamento."""
        return self.training_jobs.get(job_id)

    def list_training_jobs(self) -> List[TrainingJob]:
        """Lista todos os jobs de treinamento."""
        return list(self.training_jobs.values())
