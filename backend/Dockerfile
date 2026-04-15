# backend/Dockerfile
# Build context: raiz do projeto (docker-compose context: .)
# Multi-stage build: reduz tamanho da imagem final

# Stage 1: Builder — instala dependências
FROM python:3.11-slim AS builder

WORKDIR /app

# Copiar requirements primeiro (layer caching)
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime — imagem final enxuta
FROM python:3.11-slim

WORKDIR /app

# Copiar site-packages do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar o pacote backend mantendo a estrutura (backend/main.py → /app/backend/main.py)
# Necessário para imports relativos (from .config import settings) e uvicorn backend.main:app
COPY . .

# Porta exposta
EXPOSE 8001

# Health check (start_period generoso para cold start)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Entry point
CMD ["python", "backend/main.py"]
