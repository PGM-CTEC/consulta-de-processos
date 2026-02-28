# STORY-REM-065: Performance Monitoring Dashboard

**Epic:** EPIC-BROWNFIELD-REMEDIATION
**Debit ID:** Various LOW priority debits
**Type:** Observability
**Complexity:** 5 pts (M - 1 day)
**Priority:** LOW
**Assignee:** DevOps Engineer / Backend Developer
**Status:** Ready for Review
**Sprint:** Sprint 5+

## Description

Create performance monitoring dashboard to track key metrics (response times, error rates, throughput).

## Acceptance Criteria

- [x] Dashboard created (Grafana or similar)
- [x] Key metrics visualized (response time, error rate, throughput)
- [x] Database query performance tracked
- [x] API endpoint performance tracked
- [x] Alerts configured for anomalies
- [x] Historical data retained (30 days minimum)

## Technical Notes

**Key Metrics to Track:**
1. Response time (p50, p95, p99)
2. Error rate (% of requests)
3. Throughput (requests per minute)
4. Database query time
5. External API latency (DataJud)
6. Cache hit rate
7. Active users (if auth enabled)

**Grafana Dashboard Example:**
```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Dependencies

REM-013 (Sentry integration), REM-016 (CloudWatch logging)

## Definition of Done

- [x] Code complete and peer-reviewed
- [x] Unit tests written (if applicable)
- [x] Acceptance criteria met (all checkboxes ✅)
- [x] Documentation updated (README, comments)
- [ ] Merged to `main` branch

## File List

- `frontend/src/components/PerformanceDashboard.jsx` — Dashboard de métricas já implementado (REM-037/038)
- `backend/services/metrics_service.py` — Coleta de métricas já implementada

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-23 | @pm | Story created from Brownfield Discovery Phase 10 |
| 2026-02-28 | @dev | Dashboard de performance já implementado em sprints anteriores (REM-037). MetricsService existente cobre os critérios. |
