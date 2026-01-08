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

from io import BytesIO

from fastapi import APIRouter, Depends
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
        500: {
            "description": "Error al generar el PDF",
        },
    },
)
async def generar_comprobante_postulacion(
    request: ComprobantePostulacionRequest,
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
    # 1. Convertir schemas Pydantic → DTOs de aplicación
    # Solo pasamos campos requeridos explícitamente
    # Los campos opcionales usan los defaults de los DTOs
    comprobante_dto = ComprobantePostulacionDTO(
        estudiante=EstudianteDTO(
            nombre=request.estudiante.nombre,
            apellido=request.estudiante.apellido,
            dni=request.estudiante.dni,
            email=request.estudiante.email,
            cuil=request.estudiante.cuil,
            fecha_nacimiento=request.estudiante.fecha_nacimiento,
            tipo_dni=request.estudiante.tipo_dni,
        ),
        universidad=UniversidadDTO(
            nombre=request.universidad.nombre,
            direccion=request.universidad.direccion,
            codigo_postal=request.universidad.codigo_postal,
            correo=request.universidad.correo,
            telefono=request.universidad.telefono,
        ),
        carrera=CarreraDTO(
            nombre=request.carrera.nombre,
            codigo=request.carrera.codigo,
            descripcion=request.carrera.descripcion,
            plan_estudios=request.carrera.plan_estudios,
        ),
        empresa=EmpresaDTO(
            nombre=request.empresa.nombre,
            direccion=request.empresa.direccion,
            codigo_postal=request.empresa.codigo_postal,
            telefono=request.empresa.telefono,
            codigo=request.empresa.codigo,
        ),
        proyecto=ProyectoDTO(
            nombre=request.proyecto.nombre,
            fecha_inicio=request.proyecto.fecha_inicio,
            descripcion=request.proyecto.descripcion,
            numero=request.proyecto.numero,
            estado=request.proyecto.estado,
            fecha_fin=request.proyecto.fecha_fin,
        ),
        puesto=PuestoDTO(
            nombre=request.puesto.nombre,
            descripcion=request.puesto.descripcion,
            codigo=request.puesto.codigo,
            horas_dedicadas=request.puesto.horas_dedicadas,
        ),
        postulacion=PostulacionDTO(
            numero=request.postulacion.numero,
            fecha=request.postulacion.fecha,
            cantidad_materias_aprobadas=request.postulacion.cantidad_materias_aprobadas,
            cantidad_materias_regulares=request.postulacion.cantidad_materias_regulares,
            estado=request.postulacion.estado,
        ),
    )
    
    # 2. Ejecutar el use case para generar el PDF
    result = use_case.execute(comprobante_dto)
    
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
        500: {
            "description": "Error al generar el PDF",
        },
    },
)
async def generar_comprobante_contrato(
    request: ComprobanteContratoRequest,
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
    # 1. Convertir schemas Pydantic → DTOs de aplicación
    comprobante_dto = ComprobanteContratoDTO(
        estudiante=EstudianteDTO(
            nombre=request.estudiante.nombre,
            apellido=request.estudiante.apellido,
            email=request.estudiante.email,
            dni=request.estudiante.dni,
            cuil=request.estudiante.cuil,
            fecha_nacimiento=request.estudiante.fecha_nacimiento,
            tipo_dni=request.estudiante.tipo_dni,
        ),
        universidad=UniversidadDTO(
            nombre=request.universidad.nombre,
            direccion=request.universidad.direccion,
            codigo_postal=request.universidad.codigo_postal,
            correo=request.universidad.correo,
            telefono=request.universidad.telefono,
        ),
        carrera=CarreraDTO(
            nombre=request.carrera.nombre,
            codigo=request.carrera.codigo,
            descripcion=request.carrera.descripcion,
            plan_estudios=request.carrera.plan_estudios,
        ),
        empresa=EmpresaDTO(
            nombre=request.empresa.nombre,
            direccion=request.empresa.direccion,
            codigo_postal=request.empresa.codigo_postal,
            telefono=request.empresa.telefono,
            codigo=request.empresa.codigo,
        ),
        proyecto=ProyectoDTO(
            nombre=request.proyecto.nombre,
            descripcion=request.proyecto.descripcion,
            numero=request.proyecto.numero,
            estado=request.proyecto.estado,
            fecha_inicio=request.proyecto.fecha_inicio,
            fecha_fin=request.proyecto.fecha_fin,
        ),
        puesto=PuestoDTO(
            nombre=request.puesto.nombre,
            descripcion=request.puesto.descripcion,
            codigo=request.puesto.codigo,
            horas_dedicadas=request.puesto.horas_dedicadas,
        ),
        postulacion=PostulacionDTO(
            numero=request.postulacion.numero,
            fecha=request.postulacion.fecha,
            estado=request.postulacion.estado,
            cantidad_materias_aprobadas=request.postulacion.cantidad_materias_aprobadas,
            cantidad_materias_regulares=request.postulacion.cantidad_materias_regulares,
        ),
        contrato=ContratoDTO(
            numero=request.contrato.numero,
            fecha_inicio=request.contrato.fecha_inicio,
            fecha_fin=request.contrato.fecha_fin,
            fecha_emision=request.contrato.fecha_emision,
            estado=request.contrato.estado,
        ),
    )
    
    # 2. Ejecutar el use case para generar el PDF
    result = use_case.execute(comprobante_dto)
    
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
async def health_check():
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
