# ================================
# Application DTOs
# ================================
# Data Transfer Objects: objetos para transferir datos
# entre capas de la aplicación.
#
# Los DTOs son diferentes de las entidades:
# - No tienen comportamiento ni reglas de negocio
# - Son simples contenedores de datos
# - Pueden ser validados con Pydantic en la capa de presentación
# ================================

from .pdf_request_dto import (
    PDFRequestDTO,
    PDFSectionDTO,
    PDFTableDTO,
    PDFStyleDTO,
)

from .business_dtos import (
    EstudianteDTO,
    UniversidadDTO,
    CarreraDTO,
    EmpresaDTO,
    ProyectoDTO,
    PuestoDTO,
    PostulacionDTO,
    ContratoDTO,
)

from .receipt_dto import ComprobantePostulacionDTO
from .agreement_dto import ComprobanteContratoDTO

__all__ = [
    # DTOs genéricos de PDF
    "PDFRequestDTO",
    "PDFSectionDTO",
    "PDFTableDTO",
    "PDFStyleDTO",
    # DTOs de negocio (entidades de Golang)
    "EstudianteDTO",
    "UniversidadDTO",
    "CarreraDTO",
    "EmpresaDTO",
    "ProyectoDTO",
    "PuestoDTO",
    "PostulacionDTO",
    "ContratoDTO",
    # DTOs compuestos para endpoints
    "ComprobantePostulacionDTO",
    "ComprobanteContratoDTO",
]
