"""
PDF Schemas
===========

Schemas Pydantic para validación de requests y responses de la API HTTP.

IMPORTANTE: Diferencia entre Schemas y DTOs en Clean Architecture
------------------------------------------------------------------

**SCHEMAS (este archivo - Presentation Layer):**
- Propósito: Validación HTTP y serialización de datos externos
- Framework: Pydantic (dependiente de FastAPI)
- Responsabilidades:
  * Validar formato de entrada HTTP (regex, rangos, tipos)
  * Generar documentación OpenAPI automática
  * Serializar/deserializar JSON ↔ Python
  * Contener ejemplos para la documentación
- Ubicación: `presentation/schemas/`
- Naming: Sufijo "Schema" o "Request"/"Response"

**DTOs (application/dto/ - Application Layer):**
- Propósito: Transferir datos entre capas internas
- Framework: Dataclasses simples (independiente del framework web)
- Responsabilidades:
  * Transportar datos entre Presentation → Application → Domain
  * NO contienen validaciones (ya se hicieron en Schemas)
  * Son mapeados a/desde entidades del dominio
- Ubicación: `application/dto/`
- Naming: Sufijo "DTO"

**Flujo de datos típico:**
1. HTTP Request (JSON) → Schema valida y parsea
2. Schema → DTO (mapping simple en el controlador)
3. DTO → Caso de Uso → Entidad de Dominio
4. Entidad → DTO → Schema Response
5. Schema Response → HTTP Response (JSON)

**¿Cuándo usar cada uno?**
- Usa SCHEMAS para todo lo que entra/sale por HTTP
- Usa DTOs para comunicación interna entre capas
- NUNCA expongas DTOs directamente en endpoints HTTP
- NUNCA pases Schemas a los casos de uso
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PDFTableSchema(BaseModel):
    """Schema para una tabla en el PDF."""
    
    headers: list[str] = Field(
        ...,
        min_length=1,
        description="Encabezados de la tabla",
        examples=[["Nombre", "Cantidad", "Precio"]],
    )
    rows: list[list[str]] = Field(
        default_factory=list,
        description="Filas de datos",
        examples=[[["Producto A", "10", "$100"], ["Producto B", "5", "$50"]]],
    )
    title: str | None = Field(
        default=None,
        description="Título opcional de la tabla",
    )
    
    @field_validator("rows")
    @classmethod
    def validate_rows(cls, v: list[list[str]], info) -> list[list[str]]:
        """Valida que todas las filas tengan el mismo número de columnas."""
        if not v:
            return v
        
        # Obtener headers del contexto de validación
        headers = info.data.get("headers", [])
        if headers:
            expected_cols = len(headers)
            for i, row in enumerate(v):
                if len(row) != expected_cols:
                    raise ValueError(
                        f"La fila {i} tiene {len(row)} columnas, "
                        f"pero los headers tienen {expected_cols}"
                    )
        return v


class PDFSectionSchema(BaseModel):
    """Schema para una sección del documento."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Título de la sección",
        examples=["Introducción"],
    )
    content: str | None = Field(
        default=None,
        max_length=50000,
        description="Contenido de texto de la sección",
    )
    level: int = Field(
        default=1,
        ge=1,
        le=6,
        description="Nivel del encabezado (1-6)",
    )
    tables: list[PDFTableSchema] = Field(
        default_factory=list,
        description="Tablas dentro de la sección",
    )


class PDFStyleSchema(BaseModel):
    """Schema para estilos del PDF."""
    
    primary_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Color primario en formato hexadecimal",
        examples=["#1a73e8"],
    )
    text_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Color del texto en formato hexadecimal",
        examples=["#333333"],
    )
    font_family: Literal["Helvetica", "Times-Roman", "Courier"] | None = Field(
        default=None,
        description="Familia de fuente",
    )
    font_size: float | None = Field(
        default=None,
        ge=6,
        le=72,
        description="Tamaño de fuente base (puntos)",
    )
    margin_top: float | None = Field(
        default=None,
        ge=0,
        le=300,
        description="Margen superior (puntos)",
    )
    margin_bottom: float | None = Field(
        default=None,
        ge=0,
        le=300,
        description="Margen inferior (puntos)",
    )
    margin_left: float | None = Field(
        default=None,
        ge=0,
        le=300,
        description="Margen izquierdo (puntos)",
    )
    margin_right: float | None = Field(
        default=None,
        ge=0,
        le=300,
        description="Margen derecho (puntos)",
    )


class PDFGenerateRequest(BaseModel):
    """
    Request para generar un PDF.
    
    Este es el schema principal que recibe el endpoint POST /api/v1/pdf/generate.
    """
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Título del documento",
        examples=["Reporte Mensual de Ventas"],
    )
    sections: list[PDFSectionSchema] = Field(
        ...,
        min_length=1,
        description="Secciones del documento",
    )
    author: str | None = Field(
        default=None,
        max_length=100,
        description="Autor del documento",
    )
    page_size: Literal["A4", "LETTER", "LEGAL", "A3", "A5"] = Field(
        default="A4",
        description="Tamaño de página",
    )
    orientation: Literal["portrait", "landscape"] = Field(
        default="portrait",
        description="Orientación de la página",
    )
    style: PDFStyleSchema | None = Field(
        default=None,
        description="Estilos opcionales del PDF",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Metadatos adicionales",
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Reporte de Ventas Q4 2024",
                    "sections": [
                        {
                            "title": "Resumen Ejecutivo",
                            "content": "Este reporte presenta los resultados...",
                            "level": 1,
                        },
                        {
                            "title": "Datos de Ventas",
                            "level": 1,
                            "tables": [
                                {
                                    "headers": ["Producto", "Unidades", "Ingresos"],
                                    "rows": [
                                        ["Widget A", "1000", "$50,000"],
                                        ["Widget B", "500", "$25,000"],
                                    ],
                                    "title": "Ventas por Producto",
                                }
                            ],
                        },
                    ],
                    "author": "Departamento de Ventas",
                    "page_size": "A4",
                    "orientation": "portrait",
                }
            ]
        }
    }


class PDFGenerateResponse(BaseModel):
    """Response de generación exitosa de PDF."""
    
    success: bool = Field(
        default=True,
        description="Indica si la operación fue exitosa",
    )
    document_id: str = Field(
        ...,
        description="ID único del documento generado",
    )
    filename: str = Field(
        ...,
        description="Nombre sugerido para el archivo",
    )
    message: str = Field(
        default="PDF generado exitosamente",
        description="Mensaje descriptivo",
    )


class ErrorResponse(BaseModel):
    """Response de error."""
    
    success: bool = Field(
        default=False,
        description="Siempre false para errores",
    )
    error: str = Field(
        ...,
        description="Código de error",
        examples=["INVALID_DOCUMENT"],
    )
    message: str = Field(
        ...,
        description="Descripción del error",
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Detalles adicionales del error",
    )
