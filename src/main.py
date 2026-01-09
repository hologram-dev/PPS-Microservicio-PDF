"""
PDF Export Microservice - Main Application
==========================================

Punto de entrada de la aplicación FastAPI.

Este archivo:
1. Configura la aplicación FastAPI
2. Registra middlewares (CORS, etc.)
3. Incluye los routers de la API
4. Define handlers de excepciones
5. Configura la documentación OpenAPI
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.domain.exceptions import DomainException
from src.infrastructure.config import get_settings
from src.presentation.api.v1 import router as v1_router


# ================================
# Lifespan (startup/shutdown)
# ================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    
    - startup: inicialización de recursos
    - shutdown: limpieza de recursos
    """
    # Startup
    settings = get_settings()
    print(f"[*] Starting {settings.app_name} v{settings.app_version}")
    print(f"[*] Environment: {settings.app_env}")
    print(f"[*] Debug: {settings.debug}")
    
    yield  # Aplicación corriendo
    
    # Shutdown
    print("[*] Shutting down...")


# ================================
# Application Factory
# ================================

def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    
    Usar un factory permite:
    - Crear múltiples instancias para testing
    - Configurar la app de forma diferente según el entorno
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
## PDF Export Microservice

Microservicio para generación de documentos PDF usando ReportLab.

### Características

- ✅ Generación programática de PDFs
- ✅ Soporte para tablas y secciones
- ✅ Estilos personalizables
- ✅ API REST simple

### Clean Architecture

Este microservicio implementa Clean Architecture:
- **Domain**: Entidades y reglas de negocio
- **Application**: Casos de uso
- **Infrastructure**: Implementaciones (ReportLab)
- **Presentation**: API REST (FastAPI)
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # ================================
    # Middlewares
    # ================================
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ================================
    # Exception Handlers
    # ================================
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, 
        exc: DomainException
    ) -> JSONResponse:
        """
        Maneja excepciones del dominio.
        
        Convierte las excepciones del dominio en respuestas HTTP apropiadas.
        """
        status_code = 400  # Bad Request por defecto
        
        # Mapear códigos de error a status codes
        status_map = {
            "DOCUMENT_NOT_FOUND": 404,
            "PDF_GENERATION_ERROR": 500,
        }
        
        status_code = status_map.get(exc.code, 400)
        
        return JSONResponse(
            status_code=status_code,
            content=exc.to_dict(),
        )
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(
        request: Request,
        exc: RateLimitExceeded
    ) -> JSONResponse:
        """
        Maneja excepciones de rate limiting.
        
        Retorna HTTP 429 cuando se excede el límite de requests.
        """
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Demasiados requests. Por favor intente nuevamente más tarde.",
            },
        )
    
    # ================================
    # Routers
    # ================================
    
    # API v1
    app.include_router(v1_router, prefix="/api/v1")
    
    # ================================
    # Root Endpoints
    # ================================
    
    @app.get("/", tags=["Root"])
    async def root():
        """Endpoint raíz con información del servicio."""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }
    
    @app.get("/health", tags=["Health"])
    async def health():
        """Health check global del servicio."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
        }
    
    return app


# ================================
# Application Instance
# ================================

app = create_app()


# ================================
# Development Server
# ================================

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
