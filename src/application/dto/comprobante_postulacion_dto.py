"""
Comprobante de Postulación DTO
==============================

DTO compuesto que agrupa todos los DTOs necesarios para
generar el comprobante/recibo de postulación.

Este es el DTO que recibe el endpoint POST /api/v1/receipt/generate
"""

from dataclasses import dataclass

from .negocio_global_dtos import (
    EstudianteDTO,
    UniversidadDTO,
    CarreraDTO,
    EmpresaDTO,
    ProyectoDTO,
    PuestoDTO,
    PostulacionDTO,
)


@dataclass
class ComprobantePostulacionDTO:
    """
    DTO para generar el comprobante/recibo de postulación.
    
    Agrupa todos los datos que llegan desde la API Golang
    cuando el usuario solicita imprimir su comprobante.
    
    Request Body esperado:
    {
        "estudiante": { ... },
        "universidad": { ... },
        "carrera": { ... },
        "empresa": { ... },
        "proyecto": { ... },
        "puesto": { ... },
        "postulacion": { ... }
    }
    """
    estudiante: EstudianteDTO
    universidad: UniversidadDTO
    carrera: CarreraDTO
    empresa: EmpresaDTO
    proyecto: ProyectoDTO
    puesto: PuestoDTO
    postulacion: PostulacionDTO
