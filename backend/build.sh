#!/bin/bash

CONTAINER_NAME=consulta-de-processos
IMAGE_NAME=consulta-de-processos

echo "🔨 Buildando a imagem..."
docker build -t $IMAGE_NAME .

echo "➡️ Parando container antigo (se existir)..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

echo "🚀 Iniciando o container..."
docker run -d \
  -e TZ=America/Sao_Paulo \
  --name $CONTAINER_NAME \
  -p 8001:8001 \
  --restart unless-stopped \
  $IMAGE_NAME

echo "✅ Container '$CONTAINER_NAME' rodando em http://localhost:8001"