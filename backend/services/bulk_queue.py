"""
Bulk processing job queue — in-memory, asyncio-native.

Jobs are transient (not persisted across restarts). Each job processes
CNJ process numbers sequentially via asyncio with a concurrency semaphore,
updating progress counters as results arrive so the client can poll.
"""
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

logger = logging.getLogger(__name__)


@dataclass
class BulkJob:
    job_id: str
    total: int
    status: str = "pending"         # pending | running | done | error
    processed: int = 0
    failures: list = field(default_factory=list)
    results: list = field(default_factory=list)   # List[ProcessResponse] (Pydantic)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # --- helpers ---
    @property
    def failures_count(self) -> int:
        return len(self.failures)

    @property
    def results_count(self) -> int:
        return len(self.results)

    def get_results_page(self, page: int, per_page: int) -> list:
        start = (page - 1) * per_page
        return self.results[start : start + per_page]


class BulkJobManager:
    """Thread/coroutine-safe in-memory store for bulk jobs."""

    # Maximum jobs kept in memory (oldest are evicted when limit is reached).
    MAX_JOBS = 50

    def __init__(self):
        self._jobs: dict[str, BulkJob] = {}
        self._lock = asyncio.Lock()

    async def create(self, numbers: list[str]) -> BulkJob:
        async with self._lock:
            self._evict_if_needed()
            job = BulkJob(job_id=str(uuid.uuid4()), total=len(numbers))
            self._jobs[job.job_id] = job
        return job

    async def get(self, job_id: str) -> Optional[BulkJob]:
        async with self._lock:
            return self._jobs.get(job_id)

    def _evict_if_needed(self):
        """Remove oldest completed job when at capacity."""
        if len(self._jobs) < self.MAX_JOBS:
            return
        done = [(jid, j) for jid, j in self._jobs.items() if j.status in ("done", "error")]
        if done:
            oldest_id = min(done, key=lambda x: x[1].created_at)[0]
            del self._jobs[oldest_id]


# Module-level singleton shared across the application lifetime.
bulk_job_manager = BulkJobManager()


async def run_bulk_job(
    job: BulkJob,
    numbers: list[str],
    db_factory: Callable,
    max_concurrent: int,
    request_delay: float = 0.0,
    fusion_service=None,
) -> None:
    """
    Background coroutine that processes all numbers and updates the job in place.

    Creates its own db session (independent of the request session, which is
    closed when submit_bulk_job returns). Serializes each result to a Pydantic
    schema immediately while the session is still open, avoiding DetachedInstanceError
    on the polling endpoint.

    Results are appended incrementally so the polling endpoint always returns
    the latest progress without waiting for all items to finish.
    """
    from .process_service import ProcessService
    from .. import schemas

    job.status = "running"
    semaphore = asyncio.Semaphore(max_concurrent)

    db = db_factory()
    try:
        service = ProcessService(db, fusion_service=fusion_service)

        async def fetch_one(number: str):
            async with semaphore:
                if request_delay > 0:
                    await asyncio.sleep(request_delay)
                try:
                    process = await service.get_or_update_process(number)
                    if process:
                        # Serialize com schema leve (sem raw_data/movements) para
                        # reduzir tamanho da resposta de ~100 KB para ~1 KB por processo
                        serialized = schemas.ProcessBulkResult.model_validate(process)
                        return ("success", number, serialized)
                    return ("success", number, None)
                except Exception as e:
                    logger.warning(f"[bulk_job={job.job_id}] failed {number}: {e}")
                    return ("failure", number, None)

        tasks = [asyncio.create_task(fetch_one(n)) for n in numbers]

        for coro in asyncio.as_completed(tasks):
            try:
                status, number, result = await coro
            except Exception as e:
                logger.error(f"[bulk_job={job.job_id}] unexpected task error: {e}")
                job.failures.append("unknown")
                job.processed += 1
                continue

            job.processed += 1
            if status == "success" and result:
                job.results.append(result)
            else:
                job.failures.append(number)

        job.status = "done"
        job.completed_at = datetime.now()
        logger.info(
            f"[bulk_job={job.job_id}] done — "
            f"{job.results_count} ok, {job.failures_count} failed / {job.total} total"
        )
    except Exception as e:
        job.status = "error"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        logger.error(f"[bulk_job={job.job_id}] fatal error: {e}", exc_info=True)
    finally:
        db.close()
