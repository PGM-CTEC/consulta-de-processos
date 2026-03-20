# frontend/Dockerfile
# Multi-stage: Node build → Nginx serve

# Stage 1: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files primeiro (layer caching)
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copiar código e fazer build
COPY . .
RUN npm run build

# Stage 2: Runtime — Nginx serve estático
FROM nginx:alpine

# Copiar build output para nginx html dir
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config customizado (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
