#!/bin/bash
set -e

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=chatpass psql -h db -U chatuser -d chatdb -c '\q'; do
  echo "PostgreSQL no está disponible aún - esperando..."
  sleep 2
done
echo "PostgreSQL está listo!"

# Inicializar la base de datos
python init_db.py

# Ejecutar el comando especificado
exec "$@"
