"""
Database Optimization Module

Provides database performance improvements:
- Query optimization
- Index recommendations
- Connection pooling
- Query caching strategies
"""

import logging
from typing import List, Dict, Any
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization utilities."""

    @staticmethod
    def analyze_query_performance(db: Session, query_text: str) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN.

        Args:
            db: Database session
            query_text: SQL query to analyze

        Returns:
            Analysis result with performance metrics
        """
        try:
            # Execute EXPLAIN for query
            explain_query = f"EXPLAIN QUERY PLAN {query_text}"
            result = db.execute(text(explain_query))

            rows = result.fetchall()
            analysis = {
                "query": query_text,
                "plan": [dict(row._mapping) for row in rows],
                "recommendations": []
            }

            # Check for common issues
            plan_str = str(rows).lower()

            if "scan" in plan_str and "index" not in plan_str:
                analysis["recommendations"].append(
                    "⚠️ Full table scan detected - consider adding index"
                )

            if "temp" in plan_str:
                analysis["recommendations"].append(
                    "💡 Temporary table used - consider optimizing joins"
                )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_index_recommendations(db: Session) -> List[Dict[str, Any]]:
        """
        Get index recommendations for tables.

        Returns:
            List of recommended indexes
        """
        recommendations = []

        # Common query patterns that benefit from indexes
        index_patterns = [
            {
                "table": "processes",
                "column": "number",
                "reason": "Primary lookup column - frequently used in WHERE clauses",
                "type": "UNIQUE"
            },
            {
                "table": "processes",
                "column": "tribunal_name",
                "reason": "Frequently filtered by tribunal",
                "type": "INDEX"
            },
            {
                "table": "processes",
                "column": "phase",
                "reason": "Analytics queries group by phase",
                "type": "INDEX"
            },
            {
                "table": "movements",
                "column": "process_id",
                "reason": "Foreign key for joining processes and movements",
                "type": "INDEX"
            },
            {
                "table": "movements",
                "column": "date",
                "reason": "Date-based filtering and sorting",
                "type": "INDEX"
            },
            {
                "table": "search_history",
                "column": "number",
                "reason": "Lookup searches by process number",
                "type": "INDEX"
            },
            {
                "table": "search_history",
                "column": "searched_at",
                "reason": "Time-based analytics",
                "type": "INDEX"
            },
        ]

        # Check existing indexes
        inspector = inspect(db.get_bind())

        for pattern in index_patterns:
            table = pattern["table"]

            # Get existing indexes for table
            try:
                existing_indexes = inspector.get_indexes(table)
                existing_columns = {
                    col
                    for idx in existing_indexes
                    for col in idx.get("column_names", [])
                }

                # Recommend if not exists
                if pattern["column"] not in existing_columns:
                    recommendations.append({
                        "table": table,
                        "column": pattern["column"],
                        "type": pattern["type"],
                        "reason": pattern["reason"],
                        "sql": f"CREATE {pattern['type']} ON {table}({pattern['column']});"
                    })

            except Exception as e:
                logger.warning(f"Could not check indexes for {table}: {e}")

        return recommendations

    @staticmethod
    def optimize_connection_pool(engine_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize connection pool settings.

        Args:
            engine_config: Current engine configuration

        Returns:
            Optimized configuration
        """
        optimized = engine_config.copy()

        # Recommended pool settings for async workloads
        recommendations = {
            "pool_size": 10,              # Base pool size
            "max_overflow": 20,           # Additional connections on demand
            "pool_timeout": 30,           # Wait time for connection
            "pool_recycle": 3600,         # Recycle connections after 1 hour
            "pool_pre_ping": True,        # Verify connections before use
        }

        for key, value in recommendations.items():
            if key not in optimized:
                optimized[key] = value
                logger.info(f"Added pool setting: {key}={value}")

        return optimized


class QueryCache:
    """
    Simple query result cache with TTL.

    Caches frequently accessed data to reduce database load.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache.

        Args:
            ttl_seconds: Time-to-live for cached entries (default: 5 minutes)
        """
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            value, timestamp = self._cache[key]

            # Check if expired
            if datetime.now() - timestamp < self.ttl:
                self.hits += 1
                logger.debug(f"Cache hit for {key}")
                return value
            else:
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache expired for {key}")

        self.misses += 1
        return None

    def set(self, key: str, value: Any):
        """
        Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, datetime.now())
        logger.debug(f"Cached {key}")

    def invalidate(self, key: str):
        """Invalidate cache entry."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Invalidated cache for {key}")

    def clear(self):
        """Clear all cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(self._cache)
        }


class BatchQueryOptimizer:
    """Optimizes batch database operations."""

    @staticmethod
    def batch_insert(db: Session, model_class, records: List[Dict], batch_size: int = 100):
        """
        Batch insert records for better performance.

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            records: List of record dictionaries
            batch_size: Records per batch
        """
        total = len(records)
        logger.info(f"Batch inserting {total} records in batches of {batch_size}")

        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]

            # Bulk insert
            db.bulk_insert_mappings(model_class, batch)

            if (i + batch_size) % 1000 == 0:
                logger.info(f"Inserted {i + batch_size}/{total} records")

        db.commit()
        logger.info(f"Batch insert completed: {total} records")

    @staticmethod
    def batch_update(db: Session, model_class, updates: List[Dict], batch_size: int = 100):
        """
        Batch update records.

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            updates: List of update dictionaries (must include 'id')
            batch_size: Updates per batch
        """
        total = len(updates)
        logger.info(f"Batch updating {total} records in batches of {batch_size}")

        for i in range(0, total, batch_size):
            batch = updates[i:i + batch_size]
            db.bulk_update_mappings(model_class, batch)

        db.commit()
        logger.info(f"Batch update completed: {total} records")


# Global query cache instance
_query_cache = QueryCache(ttl_seconds=300)


def get_query_cache() -> QueryCache:
    """Get global query cache instance."""
    return _query_cache
