# backend/Dockerfile
# Multi-stage build: reduz tamanho da imagem final

# Stage 1: Builder — instala dependências
FROM python:3.11-slim AS builder

WORKDIR /app

# Copiar requirements primeiro (layer caching)
COPY requirements.txt requirements-runtime.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-runtime.txt

# Stage 2: Runtime — imagem final enxuta
FROM python:3.11-slim

WORKDIR /app

# Copiar site-packages do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código do backend
COPY . .

# Porta exposta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Entry point
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
