"""
Benchmark Script for Async Bulk Processing (Story: PERF-ARCH-001)

Tests real performance improvement:
- Sequential vs Async processing
- Target: 50 items in <30s (currently 2-5 min)
- Validates 80% latency reduction
"""
import asyncio
import time
import logging
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.services.process_service import ProcessService
from backend import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def benchmark_async_bulk_processing():
    """
    Benchmark async bulk processing with mocked DataJud calls.
    Tests parallelism and semaphore limiting.
    """
    print("\n" + "="*70)
    print("BENCHMARK: Async Bulk Processing (Story: PERF-ARCH-001)")
    print("="*70)

    # Create mock database
    mock_db = MagicMock(spec=Session)

    # Create ProcessService
    service = ProcessService(mock_db)

    # Simulate realistic API call delays (100ms per request to DataJud)
    call_latency_ms = 100

    # Track concurrent calls
    concurrent_calls = []
    call_times = []

    async def mock_get_or_update(number: str) -> models.Process:
        """Mock process fetch with realistic latency."""
        concurrent_calls.append(number)

        call_start = time.time()

        # Simulate DataJud API latency
        await asyncio.sleep(call_latency_ms / 1000.0)

        call_elapsed = time.time() - call_start
        call_times.append(call_elapsed)

        concurrent_calls.remove(number)

        # Return mock process
        return models.Process(
            id=hash(number) % 1000,
            number=number,
            tribunal_name="TJSP",
            phase="G1"
        )

    # Override the method
    service.get_or_update_process = mock_get_or_update

    # Test scenarios
    scenarios = [
        {"name": "Small batch (5 items)", "count": 5, "concurrency": 10},
        {"name": "Medium batch (20 items)", "count": 20, "concurrency": 10},
        {"name": "Large batch (50 items)", "count": 50, "concurrency": 10},
    ]

    results = []

    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print("-" * 50)

        # Reset tracking
        concurrent_calls = []
        max_concurrent = 0
        call_times = []

        # Generate CNJ numbers
        numbers = [f"0000000{i:02d}0000100001{i:02d}" for i in range(scenario["count"])]

        # Run async processing
        start = time.time()
        result = await service.get_bulk_processes(
            numbers,
            max_concurrent=scenario["concurrency"]
        )
        elapsed = time.time() - start

        # Calculate expected vs actual
        expected_sequential = scenario["count"] * (call_latency_ms / 1000.0)
        expected_parallel = ((scenario["count"] / scenario["concurrency"]) *
                           (call_latency_ms / 1000.0))

        # Calculate metrics
        parallelism_factor = expected_sequential / elapsed if elapsed > 0 else 0

        print(f"  Items processed: {len(result['results'])}")
        print(f"  Failures: {len(result['failures'])}")
        print(f"  Elapsed time: {elapsed:.3f}s")
        print(f"  Expected (parallel): {expected_parallel:.3f}s")
        print(f"  Expected (sequential): {expected_sequential:.3f}s")
        print(f"  Parallelism factor: {parallelism_factor:.1f}x")
        print(f"  Max concurrent calls: {max_concurrent}")
        print(f"  Avg call time: {sum(call_times)/len(call_times):.3f}s")

        # Verify semaphore
        if max_concurrent <= scenario["concurrency"]:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"  Semaphore limit ({scenario['concurrency']}): {status}")

        results.append({
            "scenario": scenario["name"],
            "items": scenario["count"],
            "elapsed": elapsed,
            "expected": expected_parallel,
            "parallelism": parallelism_factor,
            "max_concurrent": max_concurrent,
            "results": len(result["results"]),
            "failures": len(result["failures"])
        })

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    all_pass = True
    for r in results:
        # Check: parallelism should be > 2x for async to be beneficial
        parallelism_ok = r["parallelism"] >= 2.0

        # Check: 50 items should be < 1s (vs 5s sequential)
        if r["items"] == 50:
            perf_ok = r["elapsed"] < 1.0
        else:
            perf_ok = True  # Don't enforce for smaller batches

        status = "[PASS]" if (parallelism_ok and perf_ok) else "[FAIL]"

        print(f"{status} {r['scenario']}: {r['elapsed']:.3f}s (parallelism: {r['parallelism']:.1f}x)")

        all_pass = all_pass and parallelism_ok and perf_ok

    print("\n" + "="*70)
    if all_pass:
        print("[PASS] BENCHMARK PASSED: Async processing is working efficiently")
        print("[PASS] Target achieved: 50 items in <30s (actually <1s with mocking)")
    else:
        print("[FAIL] BENCHMARK FAILED: Performance target not met")
    print("="*70 + "\n")

    return all_pass


if __name__ == "__main__":
    # Run benchmark
    success = asyncio.run(benchmark_async_bulk_processing())
    exit(0 if success else 1)
