"""
API v1 Router
=============

Router principal para la versión 1 de la API.

Este archivo define los endpoints de la API.

Estructura típica de un endpoint:
1. Recibe request HTTP
2. Valida con Pydantic schemas
3. Convierte a DTOs
4. Llama al servicio de aplicación
5. Convierte respuesta a schema
6. Retorna response HTTP
"""

import asyncio
from io import BytesIO

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import StreamingResponse

from src.presentation.schemas.comprobante_postulacion_schemas import (
    ComprobantePostulacionRequest,
)
from src.presentation.schemas.comprobante_contrato_schemas import (
    ComprobanteContratoRequest,
)
from src.presentation.dependencies.container import (
    get_generar_comprobante_postulacion_use_case,
    get_generar_comprobante_contrato_use_case,
)
from src.application.dto import (
    ComprobantePostulacionDTO,
    ComprobanteContratoDTO,
    EstudianteDTO,
    UniversidadDTO,
    CarreraDTO,
    EmpresaDTO,
    ProyectoDTO,
    PuestoDTO,
    PostulacionDTO,
    ContratoDTO,
)

router = APIRouter(prefix="/pdf", tags=["PDF"])

# ================================
# Rate Limiter Configuration
# ================================
limiter = Limiter(key_func=get_remote_address)


# ================================
# Endpoints
# ================================


@router.post(
    "/generate/comprobante_postulacion",
    response_class=StreamingResponse,
    summary="Generar Comprobante de Postulación",
    description="Genera un PDF con el comprobante de postulación a partir de los datos recibidos desde la API Golang",
    responses={
        200: {
            "description": "PDF generado exitosamente",
            "content": {"application/pdf": {}},
        },
        400: {
            "description": "Datos inválidos en el request",
        },
        429: {
            "description": "Demasiados requests - Rate limit excedido",
        },
        500: {
            "description": "Error al generar el PDF",
        },
    },
)
@limiter.limit("100/minute")
async def generar_comprobante_postulacion(
    request: Request,
    data: ComprobantePostulacionRequest,
    use_case=Depends(get_generar_comprobante_postulacion_use_case),
):
    """
    Genera el comprobante de postulación en formato PDF.
    
    Este endpoint recibe los datos de la postulación desde la API Golang
    y genera un PDF profesional con toda la información.
    
    El PDF incluye:
    - Datos del estudiante
    - Datos académicos (universidad y carrera)
    - Detalles de la postulación (empresa, proyecto, puesto)
    - Estado de la postulación
    
    Args:
        request: Datos validados de la postulación
        use_case: Use case inyectado para generar el comprobante
        
    Returns:
        StreamingResponse con el PDF generado
    """
    # 1. Convertir schemas Pydantic → DTOs de aplicación usando model_dump()
    comprobante_dto = ComprobantePostulacionDTO(
        estudiante=EstudianteDTO(**data.estudiante.model_dump()),
        universidad=UniversidadDTO(**data.universidad.model_dump()),
        carrera=CarreraDTO(**data.carrera.model_dump()),
        empresa=EmpresaDTO(**data.empresa.model_dump()),
        proyecto=ProyectoDTO(**data.proyecto.model_dump()),
        puesto=PuestoDTO(**data.puesto.model_dump()),
        postulacion=PostulacionDTO(**data.postulacion.model_dump()),
    )
    
    # 2. Ejecutar el use case para generar el PDF (async con thread pool)
    result = await asyncio.to_thread(
        use_case.execute,
        comprobante_dto
    )
    
    # 3. Crear stream con el contenido del PDF
    pdf_stream = BytesIO(result.content)
    
    # 4. Retornar como streaming response
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={result.filename}",
        },
    )

@router.post(
    "/generate/comprobante_contrato",
    response_class=StreamingResponse,
    summary="Generar Comprobante de Contrato",
    description="Genera un PDF con el comprobante de contrato a partir de los datos recibidos desde la API Golang",
    responses={
        200: {
            "description": "PDF generado exitosamente",
            "content": {"application/pdf": {}},
        },
        400: {
            "description": "Datos inválidos en el request",
        },
        429: {
            "description": "Demasiados requests - Rate limit excedido",
        },
        500: {
            "description": "Error al generar el PDF",
        },
    },
)
@limiter.limit("100/minute")
async def generar_comprobante_contrato(
    request: Request,
    data: ComprobanteContratoRequest,
    use_case=Depends(get_generar_comprobante_contrato_use_case),
):
    """
    Genera el comprobante de contrato en formato PDF.
    
    Este endpoint recibe los datos de la postulación desde la API Golang
    y genera un PDF profesional con toda la información.
    
    El PDF incluye:
    - Datos del estudiante
    - Datos académicos (universidad y carrera)
    - Detalles de la postulación (empresa, proyecto, puesto)
    - Estado de la postulación
    
    Args:
        request: Datos validados de la postulación
        use_case: Use case inyectado para generar el comprobante
        
    Returns:
        StreamingResponse con el PDF generado
    """
    # 1. Convertir schemas Pydantic → DTOs de aplicación usando model_dump()
    comprobante_dto = ComprobanteContratoDTO(
        estudiante=EstudianteDTO(**data.estudiante.model_dump()),
        universidad=UniversidadDTO(**data.universidad.model_dump()),
        carrera=CarreraDTO(**data.carrera.model_dump()),
        empresa=EmpresaDTO(**data.empresa.model_dump()),
        proyecto=ProyectoDTO(**data.proyecto.model_dump()),
        puesto=PuestoDTO(**data.puesto.model_dump()),
        postulacion=PostulacionDTO(**data.postulacion.model_dump()),
        contrato=ContratoDTO(**data.contrato.model_dump()),
    )
    
    # 2. Ejecutar el use case para generar el PDF (async con thread pool)
    result = await asyncio.to_thread(
        use_case.execute,
        comprobante_dto
    )
    
    # 3. Crear stream con el contenido del PDF
    pdf_stream = BytesIO(result.content)
    
    # 4. Retornar como streaming response
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={result.filename}",
        },
    )


@router.get("/health")
@limiter.limit("200/minute")
async def health_check(request: Request):
    """
    Health check del servicio de PDF.
    
    Returns:
        Estado del servicio
    """
    return {
        "status": "healthy",
        "service": "pdf-generator",
        "version": "1.0.0",
    }
