#!/usr/bin/env python3
"""CLI tool for viewing and filtering logs."""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime


def read_logs(log_file="logs/backend.log"):
    """Read and parse JSON logs."""
    if not Path(log_file).exists():
        print(f"Log file not found: {log_file}")
        return []

    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return logs


def filter_logs(logs, level=None, process=None, service=None, time_range=None):
    """Filter logs by criteria."""
    filtered = logs

    if level:
        filtered = [l for l in filtered if l.get('level') == level]

    if process:
        filtered = [l for l in filtered if str(l.get('process_number')) == str(process)]

    if service:
        filtered = [l for l in filtered if l.get('service') == service]

    if time_range:
        # Simple time range: "2026-02-21T10:00:00" to "2026-02-21T11:00:00"
        start, end = time_range.split(',')
        filtered = [
            l for l in filtered
            if start <= l.get('timestamp', '') <= end
        ]

    return filtered


def format_json(logs):
    """Output as JSON."""
    for log in logs:
        print(json.dumps(log))


def format_table(logs):
    """Output as simple table."""
    if not logs:
        print("No logs found")
        return

    # Header
    headers = ['timestamp', 'level', 'message', 'process_number']
    print(f"{headers[0]:25} | {headers[1]:8} | {headers[2]:40} | {headers[3]:10}")
    print("-" * 95)

    for log in logs:
        timestamp = log.get('timestamp', '')[:19]
        level = log.get('level', '')[:8]
        message = log.get('message', '')[:40]
        process = str(log.get('process_number', ''))[:10]
        print(f"{timestamp:25} | {level:8} | {message:40} | {process:10}")


def format_summary(logs):
    """Output summary statistics."""
    levels = {}
    services = {}

    for log in logs:
        level = log.get('level')
        service = log.get('service')

        levels[level] = levels.get(level, 0) + 1
        services[service] = services.get(service, 0) + 1

    print(f"Total logs: {len(logs)}")
    print("\nBy Level:")
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")

    print("\nBy Service:")
    for service, count in sorted(services.items()):
        print(f"  {service}: {count}")


def main():
    parser = argparse.ArgumentParser(description='View and filter logs')
    parser.add_argument('--log-file', default='logs/backend.log', help='Log file path')
    parser.add_argument('--level', help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--process', help='Filter by process number')
    parser.add_argument('--service', help='Filter by service name')
    parser.add_argument('--time-range', help='Filter by time range (start,end in ISO format)')
    parser.add_argument('--format', choices=['json', 'table', 'summary'], default='table', help='Output format')
    parser.add_argument('--count', type=int, help='Limit number of results')

    args = parser.parse_args()

    logs = read_logs(args.log_file)
    logs = filter_logs(logs, args.level, args.process, args.service, args.time_range)

    if args.count:
        logs = logs[-args.count:]

    if args.format == 'json':
        format_json(logs)
    elif args.format == 'summary':
        format_summary(logs)
    else:
        format_table(logs)


if __name__ == '__main__':
    main()
