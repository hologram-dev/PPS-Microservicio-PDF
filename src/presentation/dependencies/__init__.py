# ================================
# Presentation Dependencies
# ================================
# Inyección de dependencias para FastAPI.
# ================================

from .container import (
    get_pdf_generator,
    get_generate_pdf_use_case,
    get_generar_comprobante_postulacion_use_case,
)

__all__ = [
    "get_pdf_generator",
    "get_generate_pdf_use_case",
    "get_generar_comprobante_postulacion_use_case",
]

