"""
Comprobante de Contrato DTO
===========================

DTO compuesto que agrupa todos los DTOs necesarios para
generar el contrato de pasantía.

Este es el DTO que recibe el endpoint POST /api/v1/agreement/generate
"""

from dataclasses import dataclass

from .business_dtos import (
    EstudianteDTO,
    UniversidadDTO,
    CarreraDTO,
    EmpresaDTO,
    ProyectoDTO,
    PuestoDTO,
    ContratoDTO,
)


@dataclass
class ComprobanteContratoDTO:
    """
    DTO para generar el contrato de pasantía.
    
    Agrupa todos los datos que llegan desde la API Golang
    cuando el usuario solicita imprimir su contrato.
    
    Request Body esperado:
    {
        "estudiante": { ... },
        "universidad": { ... },
        "carrera": { ... },
        "empresa": { ... },
        "proyecto": { ... },
        "puesto": { ... },
        "contrato": { ... }
    }
    """
    estudiante: EstudianteDTO
    universidad: UniversidadDTO
    carrera: CarreraDTO
    empresa: EmpresaDTO
    proyecto: ProyectoDTO
    puesto: PuestoDTO
    contrato: ContratoDTO
