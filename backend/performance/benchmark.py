"""
Performance Benchmarking Module

Measures and benchmarks key operations:
- Bulk process fetching
- Database queries
- API response times
- Concurrent request handling
"""

import asyncio
import time
import logging
from typing import Callable, Any, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class BenchmarkResult:
    """Holds benchmark execution result."""

    def __init__(self, name: str, duration: float, iterations: int = 1, success: bool = True):
        self.name = name
        self.duration = duration
        self.iterations = iterations
        self.success = success
        self.timestamp = datetime.now()

    @property
    def avg_time(self) -> float:
        """Average time per iteration."""
        return self.duration / self.iterations if self.iterations > 0 else 0

    @property
    def throughput(self) -> float:
        """Operations per second."""
        return self.iterations / self.duration if self.duration > 0 else 0

    def __repr__(self) -> str:
        status = "✅" if self.success else "❌"
        return (
            f"{status} {self.name}: "
            f"{self.duration:.2f}s ({self.iterations} iterations, "
            f"{self.avg_time*1000:.2f}ms avg, "
            f"{self.throughput:.1f} ops/s)"
        )


class Benchmark:
    """Simple benchmarking utility for performance testing."""

    @staticmethod
    def sync(func: Callable, *args, iterations: int = 1, **kwargs) -> BenchmarkResult:
        """
        Benchmark synchronous function.

        Args:
            func: Function to benchmark
            *args: Positional arguments
            iterations: Number of times to run
            **kwargs: Keyword arguments

        Returns:
            BenchmarkResult with timing information
        """
        logger.info(f"Benchmarking {func.__name__} ({iterations} iterations)...")

        try:
            start = time.time()
            for _ in range(iterations):
                func(*args, **kwargs)
            duration = time.time() - start

            result = BenchmarkResult(func.__name__, duration, iterations, success=True)
            logger.info(result)
            return result

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(func.__name__, 0, iterations, success=False)

    @staticmethod
    async def async_func(func: Callable, *args, iterations: int = 1, **kwargs) -> BenchmarkResult:
        """
        Benchmark asynchronous function.

        Args:
            func: Async function to benchmark
            *args: Positional arguments
            iterations: Number of times to run
            **kwargs: Keyword arguments

        Returns:
            BenchmarkResult with timing information
        """
        logger.info(f"Benchmarking async {func.__name__} ({iterations} iterations)...")

        try:
            start = time.time()
            for _ in range(iterations):
                await func(*args, **kwargs)
            duration = time.time() - start

            result = BenchmarkResult(func.__name__, duration, iterations, success=True)
            logger.info(result)
            return result

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(func.__name__, 0, iterations, success=False)

    @staticmethod
    async def concurrent(
        func: Callable,
        tasks: List[tuple],
        name: str = "concurrent_tasks"
    ) -> BenchmarkResult:
        """
        Benchmark concurrent async operations.

        Args:
            func: Async function to run concurrently
            tasks: List of (args, kwargs) tuples for each task
            name: Name for the benchmark

        Returns:
            BenchmarkResult with timing information
        """
        logger.info(f"Benchmarking {name} ({len(tasks)} concurrent tasks)...")

        try:
            start = time.time()
            coros = [func(*args, **kwargs) for args, kwargs in tasks]
            results = await asyncio.gather(*coros, return_exceptions=True)
            duration = time.time() - start

            # Check for errors
            errors = sum(1 for r in results if isinstance(r, Exception))
            success = errors == 0

            result = BenchmarkResult(name, duration, len(tasks), success=success)
            logger.info(result)
            return result

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(name, 0, len(tasks), success=False)


class PerformanceAnalyzer:
    """Analyzes performance metrics and provides recommendations."""

    # Target performance metrics
    TARGETS = {
        "bulk_50_items": 30,  # 50 items in <30s
        "single_query": 1,    # Single query <1s
        "batch_concurrent": 5,  # Batch processing with 10 concurrent <5s
    }

    @staticmethod
    def analyze(benchmark: BenchmarkResult) -> Dict[str, Any]:
        """
        Analyze benchmark result against targets.

        Args:
            benchmark: BenchmarkResult to analyze

        Returns:
            Dict with analysis and recommendations
        """
        analysis = {
            "name": benchmark.name,
            "duration": benchmark.duration,
            "avg_time": benchmark.avg_time,
            "throughput": benchmark.throughput,
            "success": benchmark.success,
            "recommendations": [],
        }

        if not benchmark.success:
            analysis["recommendations"].append("❌ Operation failed - investigate errors")
            return analysis

        # Check against targets
        target_key = benchmark.name.lower()
        if target_key in PerformanceAnalyzer.TARGETS:
            target = PerformanceAnalyzer.TARGETS[target_key]
            if benchmark.duration > target:
                analysis["recommendations"].append(
                    f"⚠️  Slow: {benchmark.duration:.1f}s vs target {target}s. "
                    f"Optimize: reduce API calls, improve concurrency, cache results"
                )
            else:
                analysis["recommendations"].append(
                    f"✅ Good: {benchmark.duration:.1f}s (target {target}s)"
                )

        # General recommendations based on throughput
        if benchmark.throughput < 1:
            analysis["recommendations"].append(
                "💡 Consider async/await patterns for better throughput"
            )

        return analysis

    @staticmethod
    def compare(before: BenchmarkResult, after: BenchmarkResult) -> Dict[str, Any]:
        """
        Compare two benchmark results.

        Args:
            before: Original benchmark
            after: Optimized benchmark

        Returns:
            Comparison with improvement metrics
        """
        improvement = ((before.duration - after.duration) / before.duration * 100)

        return {
            "before": before.duration,
            "after": after.duration,
            "improvement_percent": improvement,
            "improvement_text": f"{'✅ Improved' if improvement > 0 else '❌ Regressed'}: {abs(improvement):.1f}%",
            "before_throughput": before.throughput,
            "after_throughput": after.throughput,
            "throughput_gain": f"{((after.throughput - before.throughput) / before.throughput * 100):.1f}%"
            if before.throughput > 0
            else "N/A",
        }


# Predefined benchmarks for common scenarios
class BulkProcessBenchmark:
    """Benchmarks for bulk process operations."""

    @staticmethod
    async def benchmark_50_items(process_service) -> BenchmarkResult:
        """Benchmark fetching 50 processes (target: <30s)."""
        numbers = [f"00000001010000100{i:03d}" for i in range(50)]

        result = await Benchmark.concurrent(
            process_service.get_or_update_process,
            [(n,) for n in numbers],
            name="bulk_50_items"
        )

        return result

    @staticmethod
    async def benchmark_concurrent_limits(process_service) -> BenchmarkResult:
        """Benchmark concurrent request limiting."""
        numbers = [f"00000001010000100{i:03d}" for i in range(20)]

        result = await Benchmark.concurrent(
            process_service.get_or_update_process,
            [(n,) for n in numbers],
            name="batch_concurrent"
        )

        return result
