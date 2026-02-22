"""
Tests for async bulk processing (Story: PERF-ARCH-001)

Validates:
1. asyncio.gather() execution with semaphore
2. Concurrent request limiting (max_concurrent)
3. Error handling for individual failures
4. Performance improvement (80% target: 2-5min → <30s)
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.process_service import ProcessService
from backend import models, schemas
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
async def process_service(mock_db):
    """Create ProcessService with mocked database."""
    service = ProcessService(mock_db)
    return service


@pytest.mark.asyncio
async def test_bulk_processes_parallel_execution(process_service):
    """
    Test that bulk_processes uses asyncio.gather() for parallel execution.
    Validates semaphore limits concurrency.
    """
    # Create mock processes
    mock_processes = [
        models.Process(id=i, number=f"00000001-{i:02d}0000100001{i:02d}")
        for i in range(5)
    ]

    # Mock get_or_update_process to track calls
    call_count = 0
    concurrent_count = 0
    max_concurrent_observed = 0

    async def mock_get_or_update(number):
        nonlocal call_count, concurrent_count, max_concurrent_observed
        call_count += 1
        concurrent_count += 1
        max_concurrent_observed = max(max_concurrent_observed, concurrent_count)

        # Simulate API call delay
        await asyncio.sleep(0.1)

        concurrent_count -= 1
        return mock_processes[int(number.split('-')[1]) % len(mock_processes)]

    process_service.get_or_update_process = mock_get_or_update

    # Test with max_concurrent=2
    numbers = [f"00000001-{i:02d}0000100001{i:02d}" for i in range(5)]
    result = await process_service.get_bulk_processes(numbers, max_concurrent=2)

    # Verify all calls were made
    assert call_count == 5
    # Verify semaphore limited concurrency to 2
    assert max_concurrent_observed <= 2, f"Expected max 2 concurrent, got {max_concurrent_observed}"
    assert len(result["results"]) > 0


@pytest.mark.asyncio
async def test_bulk_processes_error_handling(process_service):
    """
    Test that individual failures don't block the entire batch.
    Validates return_exceptions=False behavior.
    """
    call_count = 0

    async def mock_get_or_update(number):
        nonlocal call_count
        call_count += 1
        if "fail" in number:
            raise Exception(f"Simulated API error for {number}")
        process = models.Process(id=call_count, number=number)
        return process

    process_service.get_or_update_process = mock_get_or_update

    numbers = [
        "00000001-010000100001" + "00",  # success
        "fail_00000001",                  # failure
        "00000001-020000100002" + "00",  # success
    ]

    result = await process_service.get_bulk_processes(numbers)

    # Verify results
    assert len(result["results"]) == 2, f"Expected 2 successes, got {len(result['results'])}"
    assert len(result["failures"]) == 1, f"Expected 1 failure, got {len(result['failures'])}"
    assert call_count == 3, f"Expected 3 calls, got {call_count}"


@pytest.mark.asyncio
async def test_bulk_processes_performance(process_service):
    """
    Test performance improvement: 50 items should complete in <30s.
    With 10 concurrent requests at 100ms each = ~500ms total (vs 5000ms sequential).

    This is a smoke test to ensure async is faster than sequential.
    """
    import time

    call_times = []

    async def mock_get_or_update(number):
        call_start = time.time()
        await asyncio.sleep(0.05)  # Simulate 50ms API call
        call_times.append(time.time() - call_start)
        return models.Process(id=1, number=number)

    process_service.get_or_update_process = mock_get_or_update

    # Test with 50 items
    numbers = [f"00000001-{i:02d}0000100001{i:02d}" for i in range(50)]

    start = time.time()
    result = await process_service.get_bulk_processes(numbers, max_concurrent=10)
    elapsed = time.time() - start

    # Verify all completed
    assert len(result["results"]) == 50

    # Verify performance: with 10 concurrent and 50 items at 50ms each
    # Sequential would be: 50 * 0.05 = 2.5s
    # Parallel (10 concurrent): ceil(50/10) * 0.05 = 0.25s
    # Allow for overhead: <1s
    assert elapsed < 1.0, f"Expected <1s, took {elapsed:.2f}s (not parallel?)"
    print(f"✓ 50 items completed in {elapsed:.2f}s (expected <1s)")


@pytest.mark.asyncio
async def test_bulk_processes_semaphore_limit(process_service):
    """
    Test that semaphore correctly limits concurrent requests.
    """
    concurrent_slots = []
    max_observed = 0

    async def mock_get_or_update(number):
        nonlocal max_observed
        concurrent_slots.append(1)
        max_observed = max(max_observed, len(concurrent_slots))

        await asyncio.sleep(0.05)

        concurrent_slots.pop()
        return models.Process(id=1, number=number)

    process_service.get_or_update_process = mock_get_or_update

    numbers = [f"number_{i}" for i in range(20)]

    # Test different concurrency limits
    for limit in [1, 5, 10]:
        max_observed = 0
        concurrent_slots = []
        await process_service.get_bulk_processes(numbers, max_concurrent=limit)
        assert max_observed <= limit, f"Expected max {limit} concurrent, got {max_observed}"
        print(f"✓ Semaphore limit {limit}: max observed = {max_observed}")


@pytest.mark.asyncio
async def test_bulk_processes_returns_schemas(process_service):
    """
    Test that return format matches BulkProcessResponse schema.
    """
    async def mock_get_or_update(number):
        return models.Process(id=1, number=number, tribunal_name="Test")

    process_service.get_or_update_process = mock_get_or_update

    numbers = ["number_1", "number_2"]
    result = await process_service.get_bulk_processes(numbers)

    # Verify result structure
    assert isinstance(result, dict)
    assert "results" in result
    assert "failures" in result
    assert isinstance(result["results"], list)
    assert isinstance(result["failures"], list)
    print(f"✓ Result schema valid: {len(result['results'])} results, {len(result['failures'])} failures")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
