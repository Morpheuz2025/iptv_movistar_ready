FROM python:3.11-slim

# Metadatos
LABEL maintainer="IPTV Movistar+ App"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 iptv && \
    mkdir -p /app /app/data && \
    chown -R iptv:iptv /app

WORKDIR /app

# Instalar dependencias del sistema en una sola capa
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements y instalar dependencias Python
COPY --chown=iptv:iptv requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copiar código de la aplicación
COPY --chown=iptv:iptv app /app/app
COPY --chown=iptv:iptv static /app/static
COPY --chown=iptv:iptv config.py /app/config.py

# Cambiar a usuario no-root
USER iptv

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health').read()" || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]