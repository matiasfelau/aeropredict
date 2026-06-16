"""
Entrada principal de FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import auth, rutas, aeropuertos, reportes, admin, prediccion

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: startup y shutdown.
    """
    # Startup
    print("🚀 AeroPredict Backend iniciando...")
    yield
    # Shutdown
    print("🛑 AeroPredict Backend finalizando...")


# Crear app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rutas.router, prefix=f"{settings.API_PREFIX}/rutas", tags=["rutas"])
app.include_router(
    aeropuertos.router, prefix=f"{settings.API_PREFIX}/aeropuertos", tags=["aeropuertos"]
)
app.include_router(
    reportes.router, prefix=f"{settings.API_PREFIX}/reportes", tags=["reportes"]
)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(prediccion.router, prefix=f"{settings.API_PREFIX}", tags=["prediccion"])


# Rutas de health check
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AeroPredict Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "AeroPredict Backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
