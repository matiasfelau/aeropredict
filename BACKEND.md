# AeroPredict Backend API

Backend FastAPI para AeroPredict que integra el pipeline ETL existente con una API REST + PostgreSQL.

## Características

✅ **FastAPI** — Framework moderno y rápido con auto-documentación OpenAPI  
✅ **PostgreSQL** — Base de datos persistente y escalable  
✅ **SQLAlchemy ORM** — Queries type-safe con migraciones Alembic  
✅ **JWT Authentication** — Endpoints protegidos con tokens  
✅ **Integración Pipeline ETL** — Carga automática desde CSVs generados por el pipeline  
✅ **Reportes y Análisis** — Endpoints para consultas, búsqueda avanzada y agregaciones  

## Requisitos

- Python 3.11+
- PostgreSQL 13+ (o usar Docker)
- pip o Poetry

## Instalación

### 1. Clonar repositorio y crear virtualenv

```bash
cd d:\Github\aeropredict\aeropredict
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt -r requirements-backend.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu configuración (DB_URL, SECRET_KEY, etc.)
```

### 4. Crear base de datos

#### Opción A: PostgreSQL local
```bash
# Crear DB manualmente o usar psql
createdb aeropredict
```

#### Opción B: Docker Compose
```bash
docker-compose up postgres
# La DB se crea automáticamente
```

### 5. Ejecutar migraciones

```bash
python -m alembic upgrade head
```

### 6. Cargar datos iniciales

```bash
python -c "
from src.backend.database import SessionLocal, engine, Base
from src.backend.models import Usuario
from src.backend.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
admin = Usuario(
    username='admin',
    email='admin@aeropredict.local',
    password_hash=hash_password('admin123'),
    activo=True
)
db.add(admin)
db.commit()
print('✅ Usuario admin creado')
db.close()
"
```

## Uso

### Desarrollo local

```bash
# Activar virtualenv
venv\Scripts\activate

# Iniciar servidor FastAPI (hot-reload)
python -m uvicorn src.backend.main:app --reload

# API disponible en http://localhost:8000
# Documentación interactiva en http://localhost:8000/docs
```

### Con Docker Compose

```bash
# Construir e iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

## Endpoints principales

### Autenticación

```bash
# Login (obtener JWT token)
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Rutas

```bash
# Listar rutas con paginación
GET /api/rutas?limit=20&offset=0

# Obtener detalle de ruta
GET /api/rutas/{id}

# Búsqueda avanzada
GET /api/rutas/buscar/avanzada?anio=2023&mes=10&factor_min=0.7&factor_max=0.95

# Búsqueda por nombre
GET /api/rutas/ruta/Bariloche
```

### Aeropuertos

```bash
# Listar aeropuertos
GET /api/aeropuertos?limit=50&offset=0

# Obtener detalle
GET /api/aeropuertos/SABE

# Búsqueda avanzada
GET /api/aeropuertos/buscar/avanzada?localidad=Buenos%20Aires
```

### Reportes y Análisis

```bash
# Ocupación por período
GET /api/reportes/ocupacion?anio=2023&mes=10

# Tendencias de ruta (últimos 12 meses)
GET /api/reportes/tendencias?ruta=Bariloche&meses=12

# Alertas de ocupación baja/elevada
GET /api/reportes/alertas

# Top rutas por tráfico
GET /api/reportes/top-rutas?periodo=mes&anio=2023&mes=10&limit=10

# Participación por aerolínea
GET /api/reportes/aerolineas?anio=2023&limit=20
```

### Admin (requiere JWT)

```bash
# Recargar datos desde pipeline (requiere token)
POST /admin/reload-data
Authorization: Bearer {token}

# Metadata del último sync (requiere token)
GET /admin/last-sync
Authorization: Bearer {token}
```

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src.backend tests/backend/

# Tests específicos
pytest tests/backend/test_auth.py -v
pytest tests/backend/test_rutas.py -v
pytest tests/backend/test_reportes.py -v
```

## Estructura de directorios

```
src/backend/
├── __init__.py
├── main.py                 # Entrada FastAPI
├── config.py               # Configuración global
├── database.py             # SQLAlchemy setup
├── models.py               # ORM models
├── schemas.py              # Pydantic schemas
├── auth.py                 # JWT y autenticación
├── dependencies.py         # Inyección de dependencias
├── routers/
│   ├── __init__.py
│   ├── auth.py            # POST /auth/login
│   ├── rutas.py           # GET /api/rutas/*
│   ├── aeropuertos.py     # GET /api/aeropuertos/*
│   ├── reportes.py        # GET /api/reportes/*
│   └── admin.py           # POST /admin/*, GET /admin/last-sync
└── loaders/
    ├── __init__.py
    └── load_data.py       # Integración con pipeline ETL
```

## Modelos de Base de Datos

### usuarios
```sql
id, username (unique), email (unique), password_hash, activo, creado_en
```

### rutas
```sql
id, anio, mes, ruta, clasificacion_vuelo, origen_localidad, origen_provincia,
destino_localidad, destino_provincia, pasajeros, asientos, vuelos, 
factor_ocupacion, creado_en, actualizado_en
```

### rutas_aerolinea
```sql
id, ruta_id (FK), aerolinea, pasajeros, asientos, vuelos, factor_ocupacion,
creado_en, actualizado_en
```

### aeropuertos
```sql
id, codigo_oaci (unique), nombre, localidad, provincia, pais, latitud, 
longitud, creado_en, actualizado_en
```

### reportes_calidad
```sql
id, fecha_generacion, total_registros, total_descartados, descartes_por_regla (JSON),
rutas_unicas, aerolineas_unicas, periodo_inicio, periodo_fin, creado_en
```

## Integración con Pipeline ETL

El data loader (`src/backend/loaders/load_data.py`) lee los CSVs generados por el pipeline:

- `data/processed/base_mensual_ruta.csv`
- `data/processed/base_mensual_ruta_aerolinea.csv`
- `data/processed/aeropuertos_limpio.csv`

Y los carga en PostgreSQL con operaciones de upsert (crear o actualizar según clave).

### Uso manual

```bash
python -c "
from src.backend.database import SessionLocal
from src.backend.loaders.load_data import cargar_datos_desde_pipeline

db = SessionLocal()
resultado = cargar_datos_desde_pipeline(db)
print(f'Rutas nuevas: {resultado[\"rutas_nuevas\"]}')
print(f'Rutas actualizadas: {resultado[\"rutas_actualizadas\"]}')
print(f'Errores: {resultado[\"errores\"]}')
db.close()
"
```

### Uso a través de API

```bash
curl -X POST http://localhost:8000/admin/reload-data \
  -H "Authorization: Bearer {token}"
```

## Variables de entorno

Ver `.env.example` para template completo:

```
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost:5432/aeropredict
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
UMBRAL_BAJA_OCUPACION=0.60
UMBRAL_OCUPACION_ELEVADA=0.85
FACTOR_MAX_VALIDO=1.05
CRECIMIENTO_TURISTICO_PCT=0.20
```

## Documentación Swagger

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estos endpoints generan documentación automática desde los docstrings.

## Troubleshooting

### "Error: relation \"usuarios\" does not exist"
→ Ejecutar migraciones: `python -m alembic upgrade head`

### "FATAL: password authentication failed for user \"aeropredict_user\""
→ Verificar DATABASE_URL en `.env` y credenciales de PostgreSQL

### "401 Unauthorized"
→ Token JWT expirado o inválido. Obtener nuevo token en POST /auth/login

### Tests fallan
→ `pip install pytest pytest-cov` y `pytest tests/backend/`

## Roadmap

- [ ] Caching con Redis para queries costosas
- [ ] Rate limiting por IP/usuario
- [ ] Audit trail de queries
- [ ] Webhooks para notificaciones de alertas
- [ ] Export a formatos (Excel, PDF)
- [ ] GraphQL endpoint alternativo
- [ ] Soporte para múltiples lenguajes (i18n)

## Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/algo`)
3. Commit cambios (`git commit -am 'Agrega algo'`)
4. Push a rama (`git push origin feature/algo`)
5. Crear Pull Request

## Licencia

MIT

---

**Hecho con ❤️ para AeroPredict**
