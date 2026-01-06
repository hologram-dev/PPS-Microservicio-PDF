"""
Dependency Injection Container
==============================

Contenedor de inyección de dependencias para FastAPI.

La inyección de dependencias en Clean Architecture:
- Conecta las implementaciones concretas con las interfaces
- Permite cambiar implementaciones sin modificar el código
- Facilita el testing con mocks

FastAPI usa el sistema Depends() para inyección de dependencias.
Este archivo define las funciones que crean las dependencias.

Ejemplo de uso en un endpoint:
    @router.post("/generate")
    async def generate_pdf(
        request: PDFGenerateRequestSchema,
        use_case: GeneratePDFUseCase = Depends(get_generate_pdf_use_case)
    ):
        result = use_case.execute(...)
        return result

NOTA: En Clean Architecture ortodoxa, NO existe una capa de "services"
adicional. Los casos de uso (use cases) SON los servicios de aplicación.
Los controladores/endpoints llaman directamente a los casos de uso.
"""

from functools import lru_cache

from src.domain.interfaces import IPDFGenerator
from src.infrastructure.pdf import ReportLabGenerator
from src.application.use_cases import GeneratePDFUseCase
from src.application.use_cases.generar_comprobante_postulacion import (
    GenerarComprobantePostulacionUseCase,
)


@lru_cache
def get_pdf_generator() -> IPDFGenerator:
    """
    Obtiene la instancia del generador de PDF.
    
    Usa lru_cache para crear un singleton.
    Aquí es donde se decide qué implementación usar.
    
    Returns:
        Implementación de IPDFGenerator
    """
    return ReportLabGenerator()


@lru_cache
def get_generate_pdf_use_case() -> GeneratePDFUseCase:
    """
    Obtiene la instancia del caso de uso GeneratePDF.
    
    Construye el grafo de dependencias:
    - GeneratePDFUseCase depende de IPDFGenerator
    - Usamos ReportLabGenerator como implementación
    
    En Clean Architecture, los casos de uso son la capa de servicios
    de aplicación. No necesitamos una capa de "services" adicional.
    
    Returns:
        Instancia de GeneratePDFUseCase
    """
    generator = get_pdf_generator()
    return GeneratePDFUseCase(generator)


@lru_cache
def get_generar_comprobante_postulacion_use_case() -> GenerarComprobantePostulacionUseCase:
    """
    Obtiene la instancia del caso de uso para generar comprobante de postulación.
    
    Construye el grafo de dependencias:
    - GenerarComprobantePostulacionUseCase depende de IPDFGenerator
    - Usamos ReportLabGenerator como implementación
    
    Returns:
        Instancia de GenerarComprobantePostulacionUseCase
    """
    generator = get_pdf_generator()
    return GenerarComprobantePostulacionUseCase(generator)



# ================================
# Ejemplo de cómo intercambiar implementaciones
# ================================
#
# Para testing:
# def get_mock_generator() -> IPDFGenerator:
#     return MockPDFGenerator()
#
# Para producción con otro generador:
# def get_pdf_generator() -> IPDFGenerator:
#     if settings.pdf_backend == "weasyprint":
#         return WeasyPrintGenerator()
#     return ReportLabGenerator()
# ================================
