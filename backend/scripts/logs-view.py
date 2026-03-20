#!/usr/bin/env python3
"""
CLI tool for viewing, filtering, and searching structured JSON logs.

Story: REM-016 — Centralized Logging (Local)

Usage examples:
    # Last 100 lines as table
    python backend/scripts/logs-view.py

    # Last 1 hour of errors
    python backend/scripts/logs-view.py --level ERROR --last 1h

    # Search for a specific CNJ process number
    python backend/scripts/logs-view.py --search "0001234-56.2023"

    # Trace a full request by its correlation ID
    python backend/scripts/logs-view.py --request-id "abc123..."

    # Summary of access log
    python backend/scripts/logs-view.py --log-file logs/access.log --format summary

    # Watch errors in real-time (like tail -f | grep ERROR)
    python backend/scripts/logs-view.py --level ERROR --tail
"""

import json
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_duration(s: str) -> timedelta:
    """Parse a duration string like '1h', '30m', '2d' into a timedelta."""
    unit = s[-1].lower()
    try:
        value = int(s[:-1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid duration: {s!r}. Use e.g. 30m, 2h, 1d")

    if unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    else:
        raise argparse.ArgumentTypeError(f"Unknown unit {unit!r}. Use m, h, or d")


def _parse_timestamp(ts: str) -> datetime | None:
    """Parse ISO-like timestamp from log entry."""
    if not ts:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(ts[:26], fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_logs(log_file: str) -> list[dict]:
    """Read and parse newline-delimited JSON log file."""
    path = Path(log_file)
    if not path.exists():
        print(f"[logs-view] Log file not found: {log_file}", file=sys.stderr)
        return []

    logs = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                # Plain-text line — wrap it
                logs.append({"message": line, "level": "INFO"})
    return logs


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_logs(
    logs: list[dict],
    level: str | None = None,
    process: str | None = None,
    service: str | None = None,
    time_range: str | None = None,
    last: str | None = None,
    search: str | None = None,
    request_id: str | None = None,
) -> list[dict]:
    """Apply all active filters and return matching log entries."""

    filtered = logs

    # Level filter
    if level:
        level_upper = level.upper()
        filtered = [e for e in filtered if (e.get("levelname") or e.get("level") or "").upper() == level_upper]

    # Process number filter
    if process:
        filtered = [e for e in filtered if str(e.get("process_number", "")) == str(process)]

    # Service filter
    if service:
        filtered = [e for e in filtered if e.get("service") == service]

    # Absolute time range filter
    if time_range:
        parts = time_range.split(",")
        if len(parts) != 2:
            print("[logs-view] --time-range expects 'start,end' in ISO format", file=sys.stderr)
        else:
            start_str, end_str = parts
            filtered = [
                e for e in filtered
                if start_str <= (e.get("timestamp") or e.get("asctime") or "") <= end_str
            ]

    # Relative time filter (e.g., last 1h)
    if last:
        try:
            delta = _parse_duration(last)
        except argparse.ArgumentTypeError as exc:
            print(f"[logs-view] {exc}", file=sys.stderr)
        else:
            cutoff = datetime.now(timezone.utc) - delta
            result = []
            for e in filtered:
                ts_str = e.get("timestamp") or e.get("asctime") or ""
                ts = _parse_timestamp(ts_str)
                if ts is None or ts >= cutoff:
                    result.append(e)
            filtered = result

    # Free-text search across all string values
    if search:
        search_lower = search.lower()
        filtered = [
            e for e in filtered
            if any(search_lower in str(v).lower() for v in e.values())
        ]

    # Correlation/request-ID filter
    if request_id:
        filtered = [
            e for e in filtered
            if e.get("correlation_id") == request_id
        ]

    return filtered


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_json(logs: list[dict]) -> None:
    for entry in logs:
        print(json.dumps(entry, ensure_ascii=False))


def format_table(logs: list[dict]) -> None:
    if not logs:
        print("No log entries found.")
        return

    headers = ["timestamp", "level", "message", "correlation_id"]
    widths = [23, 8, 60, 36]

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))

    for entry in logs:
        ts = (entry.get("timestamp") or entry.get("asctime") or "")[:23]
        level = (entry.get("levelname") or entry.get("level") or "")[:8]
        message = str(entry.get("message") or "")[:60]
        req_id = str(entry.get("correlation_id") or "")[:36]
        print(f"{ts:<23} | {level:<8} | {message:<60} | {req_id:<36}")


def format_summary(logs: list[dict]) -> None:
    if not logs:
        print("No log entries found.")
        return

    levels: dict[str, int] = {}
    services: dict[str, int] = {}
    paths: dict[str, int] = {}
    errors: list[str] = []

    for entry in logs:
        level = (entry.get("levelname") or entry.get("level") or "UNKNOWN").upper()
        levels[level] = levels.get(level, 0) + 1

        svc = entry.get("service") or entry.get("name") or "backend"
        services[svc] = services.get(svc, 0) + 1

        path = entry.get("path")
        if path:
            paths[path] = paths.get(path, 0) + 1

        if level in ("ERROR", "CRITICAL"):
            errors.append(entry.get("message", "")[:80])

    print(f"{'─'*50}")
    print(f"  Total entries : {len(logs)}")
    print(f"{'─'*50}")

    print("\nBy Level:")
    for lvl in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        count = levels.get(lvl, 0)
        bar = "█" * min(count, 40)
        print(f"  {lvl:<10} {count:>6}  {bar}")

    if services:
        print("\nBy Service:")
        for svc, count in sorted(services.items(), key=lambda x: -x[1])[:10]:
            print(f"  {svc:<25} {count:>6}")

    if paths:
        print("\nTop 10 Endpoints:")
        for path, count in sorted(paths.items(), key=lambda x: -x[1])[:10]:
            print(f"  {path:<40} {count:>6}")

    if errors:
        print(f"\nLast {min(len(errors), 5)} Errors:")
        for msg in errors[-5:]:
            print(f"  ✗ {msg}")

    print(f"{'─'*50}")


# ---------------------------------------------------------------------------
# Tail mode
# ---------------------------------------------------------------------------

def tail_logs(log_file: str, level: str | None, search: str | None) -> None:
    """Follow a log file in real-time (like tail -f)."""
    path = Path(log_file)
    if not path.exists():
        print(f"[logs-view] Waiting for {log_file} …", file=sys.stderr)
        while not path.exists():
            time.sleep(0.5)

    print(f"[logs-view] Following {log_file} (Ctrl+C to stop)\n")
    with path.open("r", encoding="utf-8") as f:
        f.seek(0, 2)  # Jump to end
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.2)
                    continue
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    entry = {"message": line, "level": "INFO"}

                lvl = (entry.get("levelname") or entry.get("level") or "").upper()
                msg = str(entry.get("message") or "")

                if level and lvl != level.upper():
                    continue
                if search and search.lower() not in json.dumps(entry).lower():
                    continue

                ts = (entry.get("timestamp") or "")[:23]
                print(f"{ts} [{lvl:<8}] {msg}")
        except KeyboardInterrupt:
            print("\n[logs-view] Stopped.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="View and search structured JSON logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--log-file", default="logs/backend.log", help="Log file path (default: logs/backend.log)")
    parser.add_argument("--level", help="Filter by log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    parser.add_argument("--process", help="Filter by CNJ process number")
    parser.add_argument("--service", help="Filter by service name")
    parser.add_argument("--time-range", help="Absolute time range 'start,end' in ISO format")
    parser.add_argument("--last", metavar="DURATION", help="Relative time: e.g. 30m, 2h, 1d")
    parser.add_argument("--search", metavar="TEXT", help="Free-text search across all log fields")
    parser.add_argument("--request-id", metavar="UUID", help="Filter by correlation ID (X-Request-ID)")
    parser.add_argument("--format", choices=["json", "table", "summary"], default="table")
    parser.add_argument("--count", type=int, help="Show last N entries")
    parser.add_argument("--tail", action="store_true", help="Follow log file in real-time (like tail -f)")

    args = parser.parse_args()

    if args.tail:
        tail_logs(args.log_file, args.level, args.search)
        return

    logs = read_logs(args.log_file)
    logs = filter_logs(
        logs,
        level=args.level,
        process=args.process,
        service=args.service,
        time_range=args.time_range,
        last=args.last,
        search=args.search,
        request_id=args.request_id,
    )

    if args.count:
        logs = logs[-args.count:]

    if args.format == "json":
        format_json(logs)
    elif args.format == "summary":
        format_summary(logs)
    else:
        format_table(logs)


if __name__ == "__main__":
    main()
