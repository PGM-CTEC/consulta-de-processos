"""
Performance Metrics Collection Service

Collects and manages real-time performance metrics with historical trending
and alert system for performance degradation.

Metrics tracked:
- Request latency (p50, p95, p99)
- Throughput (requests/sec)
- Error rate (%)
- Database query time
- Cache hit ratio
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Single point-in-time metric snapshot."""
    timestamp: datetime
    latency_p50: float  # milliseconds
    latency_p95: float
    latency_p99: float
    throughput: float   # requests/sec
    error_rate: float   # percentage
    db_query_time: float  # milliseconds
    cache_hit_ratio: float  # percentage


class MetricsService:
    """Collects and tracks performance metrics in real-time."""

    def __init__(self, history_hours: int = 24):
        self.history_hours = history_hours
        self.history: deque = deque(maxlen=history_hours * 60)  # 1 entry per minute max

        # Current session metrics
        self.request_times: deque = deque(maxlen=1000)  # Last 1000 requests
        self.request_count = 0
        self.error_count = 0
        self.db_query_times: deque = deque(maxlen=500)
        self.cache_hits = 0
        self.cache_misses = 0

        # Alert thresholds
        self.alert_thresholds = {
            'latency_p99': 5000,  # 5 seconds
            'error_rate': 5.0,    # 5%
            'cache_hit_ratio': 0.70,  # 70%
        }

        self.active_alerts: List[Dict[str, Any]] = []

    def record_request(self, duration_ms: float, success: bool = True, db_time: float = 0.0):
        """Record a request metric."""
        self.request_times.append(duration_ms)
        self.request_count += 1
        if not success:
            self.error_count += 1
        if db_time > 0:
            self.db_query_times.append(db_time)

    def record_cache_hit(self, hit: bool):
        """Record cache hit/miss."""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def _calculate_percentile(self, data: deque, percentile: float) -> float:
        """Calculate percentile from deque of values."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return float(sorted_data[min(index, len(sorted_data) - 1)])

    def get_current_metrics(self) -> Optional[MetricSnapshot]:
        """Get current performance metrics."""
        if not self.request_times:
            return None

        # Calculate latency percentiles
        latency_p50 = self._calculate_percentile(self.request_times, 50)
        latency_p95 = self._calculate_percentile(self.request_times, 95)
        latency_p99 = self._calculate_percentile(self.request_times, 99)

        # Calculate throughput (requests per second over last minute)
        throughput = self.request_count / 60.0 if self.request_count > 0 else 0.0

        # Calculate error rate
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0

        # Calculate average DB query time
        avg_db_time = (
            sum(self.db_query_times) / len(self.db_query_times)
            if self.db_query_times
            else 0.0
        )

        # Calculate cache hit ratio
        total_cache_ops = self.cache_hits + self.cache_misses
        cache_hit_ratio = (
            self.cache_hits / total_cache_ops * 100
            if total_cache_ops > 0
            else 0.0
        )

        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            latency_p50=round(latency_p50, 2),
            latency_p95=round(latency_p95, 2),
            latency_p99=round(latency_p99, 2),
            throughput=round(throughput, 2),
            error_rate=round(error_rate, 2),
            db_query_time=round(avg_db_time, 2),
            cache_hit_ratio=round(cache_hit_ratio, 2),
        )

        # Check for alerts
        self._check_alerts(snapshot)

        # Store in history
        self.history.append(snapshot)

        return snapshot

    def _check_alerts(self, snapshot: MetricSnapshot):
        """Check if metrics exceed alert thresholds."""
        current_time = datetime.now()

        # Check latency p99
        if snapshot.latency_p99 > self.alert_thresholds['latency_p99']:
            self._add_alert(
                'LATENCY_HIGH',
                f"P99 latency {snapshot.latency_p99}ms exceeds threshold {self.alert_thresholds['latency_p99']}ms",
                'warning'
            )

        # Check error rate
        if snapshot.error_rate > self.alert_thresholds['error_rate']:
            self._add_alert(
                'ERROR_RATE_HIGH',
                f"Error rate {snapshot.error_rate}% exceeds threshold {self.alert_thresholds['error_rate']}%",
                'critical'
            )

        # Check cache hit ratio
        if snapshot.cache_hit_ratio < self.alert_thresholds['cache_hit_ratio']:
            self._add_alert(
                'CACHE_HIT_LOW',
                f"Cache hit ratio {snapshot.cache_hit_ratio}% below threshold {self.alert_thresholds['cache_hit_ratio']}%",
                'info'
            )

    def _add_alert(self, alert_type: str, message: str, severity: str):
        """Add an alert if not already present."""
        # Check if similar alert exists in last 5 minutes
        cutoff_time = datetime.now() - timedelta(minutes=5)
        for alert in self.active_alerts:
            if alert['type'] == alert_type and alert['timestamp'] > cutoff_time:
                return  # Don't add duplicate alerts

        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(),
        }
        self.active_alerts.append(alert)

        # Keep only last 50 alerts
        if len(self.active_alerts) > 50:
            self.active_alerts.pop(0)

        logger.warning(f"Performance alert: {alert_type} - {message}")

    def get_history(self, hours: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get historical metrics."""
        if hours is None:
            hours = self.history_hours

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            asdict(snapshot)
            for snapshot in self.history
            if snapshot.timestamp >= cutoff_time
        ]

    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return [
            {
                'type': alert['type'],
                'message': alert['message'],
                'severity': alert['severity'],
                'timestamp': alert['timestamp'].isoformat(),
            }
            for alert in list(self.active_alerts)[-limit:]
        ]

    def reset_session(self):
        """Reset session metrics (called every minute)."""
        self.request_count = 0
        self.error_count = 0

    def set_alert_threshold(self, metric: str, threshold: float):
        """Update alert threshold for a metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            logger.info(f"Alert threshold for {metric} set to {threshold}")


# Global metrics service instance
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get or create global metrics service."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service
