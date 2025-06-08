# syntax=docker/dockerfile:1.4

# Usamos la imagen oficial de Python 3.12-slim como base
FROM python:3.12-slim as builder

# Instalamos dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Creamos y activamos el entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa final ---
FROM python:3.12-slim

# Instalamos dependencias del sistema necesarias para WeasyPrint y PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el entorno virtual desde el builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Creamos un usuario no root para mayor seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Configuramos el directorio de trabajo
WORKDIR /app

# Copiamos el código de la aplicación
COPY . .

# Creamos directorio para la base de datos y damos permisos
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Copiamos y damos permisos al script de entrada
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Cambiamos al usuario no root
USER appuser

# Configuramos el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto
CMD ["python", "app.py", "ask", "Hola CEO‑Python"]

