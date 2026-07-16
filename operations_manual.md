# Enterprise Multi-Agent BI Platform - Operations & Troubleshooting Manual

This runbook guides operators on health checks, monitoring configurations, secret rotations, and emergency database recovery.

---

## 1. System Health Checklist
- **Backend API status:** `GET http://localhost:8000/api/v1/workflow/health`
- **RAG Knowledge Base status:** `GET http://localhost:8000/api/v1/rag/health`
- **Docker health check status:** Check status column of `docker ps` to verify all services say `(healthy)`.

---

## 2. Monitoring & Logging
The platform integrates standard Prometheus exporter endpoints and Grafana dashboards tracking:
- **API Response Latencies:** Tracked via `fastapi_requests_duration_seconds` metric.
- **Model Forecaster Accuracy:** Tracked via MLflow model registry artifacts.
- **Distributed Cache Hits:** Verified using Redis memory monitors.

---

## 3. Secret Rotations and Safety
1. **JWT Secret:** Re-generate using:
   ```bash
   openssl rand -hex 32
   ```
   Apply to `.env` as `JWT_SECRET_KEY` and restart backend pods.
2. **Database Passwords:** Update credentials in `.env` database connection string URL and PG instance simultaneously.

---

## 4. Troubleshooting Directory

### Issue: "Redis get error: Connection refused"
- **Cause:** Redis container is down or socket timeout has expired.
- **Action:** Check status of container `bi_prod_redis` using `docker logs bi_prod_redis`. Verify port `6379` is open.

### Issue: "ChromaDB query list index out of range"
- **Cause:** Collection index is empty or incomplete mock parameters returned.
- **Action:** Run catalog re-index route `POST /api/v1/catalog/reindex` to force embeddings regeneration.
