#!/bin/bash

# Script de startup para AeroPredict Backend
set -e

echo "🚀 Iniciando AeroPredict Backend..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "✅ PostgreSQL está listo"

# Ejecutar migraciones Alembic
echo "🔄 Ejecutando migraciones..."
python -m alembic upgrade head

# Inicializar datos (usuario admin)
echo "👤 Inicializando datos..."
python -c "
from src.backend.database import SessionLocal, engine, Base
from src.backend.models import Usuario
from src.backend.auth import hash_password

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear usuario admin si no existe
db = SessionLocal()
admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
if not admin:
    admin = Usuario(
        username='admin',
        email='admin@aeropredict.local',
        password_hash=hash_password('admin123'),
        activo=True
    )
    db.add(admin)
    db.commit()
    print('✅ Usuario admin creado (username: admin, password: admin123)')
else:
    print('ℹ️ Usuario admin ya existe')
db.close()
"

# Iniciar uvicorn
echo "🎯 Iniciando FastAPI..."
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
