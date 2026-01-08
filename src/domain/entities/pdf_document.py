"""
PDF Document Entity
==================

Entidad principal del dominio que representa un documento PDF.

Una entidad en Clean Architecture:
- Tiene identidad única (id)
- Encapsula reglas de negocio
- Es independiente de frameworks
- Puede cambiar su estado interno

Decisiones técnicas:
- Se usa dataclass para simplicidad y type hints
- Los campos opcionales tienen valores por defecto
- Se incluyen métodos de validación del dominio
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class PageSize(str, Enum):
    """Tamaños de página soportados."""
    A4 = "A4"
    LETTER = "LETTER"
    LEGAL = "LEGAL"
    A3 = "A3"
    A5 = "A5"


class PageOrientation(str, Enum):
    """Orientación de la página."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class PDFSection:
    """
    Representa una sección del documento PDF.
    
    Una sección puede contener:
    - Título
    - Contenido de texto
    - Elementos anidados (tablas, imágenes, etc.)
    - Metadata adicional para control de renderizado
    """
    title: str
    content: str = ""
    level: int = 1  # Nivel de encabezado (1-6)
    elements: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)  # Metadatos para control de renderizado
    
    def __post_init__(self) -> None:
        """Validaciones del dominio."""
        if self.level < 1 or self.level > 6:
            raise ValueError("El nivel de sección debe estar entre 1 y 6")


@dataclass
class PDFTable:
    """
    Representa una tabla en el documento PDF.
    
    Contiene headers y filas de datos.
    """
    headers: list[str]
    rows: list[list[str]]
    title: str | None = None
    
    def __post_init__(self) -> None:
        """Validaciones del dominio."""
        if not self.headers:
            raise ValueError("La tabla debe tener al menos un header")
        
        # Validar que todas las filas tengan el mismo número de columnas
        expected_cols = len(self.headers)
        for i, row in enumerate(self.rows):
            if len(row) != expected_cols:
                raise ValueError(
                    f"La fila {i} tiene {len(row)} columnas, "
                    f"pero se esperaban {expected_cols}"
                )


@dataclass
class PDFDocument:
    """
    Entidad principal: representa un documento PDF.
    
    Esta entidad encapsula toda la información necesaria para
    generar un documento PDF, independiente de la implementación
    de generación (ReportLab, WeasyPrint, etc.).
    
    Atributos:
        id: Identificador único del documento
        title: Título del documento
        author: Autor del documento
        created_at: Fecha de creación
        page_size: Tamaño de página
        orientation: Orientación de la página
        sections: Lista de secciones del documento
        metadata: Metadatos adicionales
    
    Ejemplo de uso:
        >>> doc = PDFDocument(
        ...     title="Reporte Mensual",
        ...     author="Sistema"
        ... )
        >>> doc.add_section(PDFSection(title="Introducción", content="..."))
    """
    
    # Atributos requeridos
    title: str
    
    # Atributos con valores por defecto
    id: UUID = field(default_factory=uuid4)
    author: str = "System"
    created_at: datetime = field(default_factory=datetime.now)
    page_size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.PORTRAIT
    sections: list[PDFSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Atributos privados para estado interno
    _is_generated: bool = field(default=False, repr=False)
    
    def __post_init__(self) -> None:
        """Validaciones del dominio al crear la entidad."""
        if not self.title or not self.title.strip():
            raise ValueError("El título del documento es requerido")
    
    # ================================
    # Métodos de comportamiento
    # ================================
    
    def add_section(self, section: PDFSection) -> None:
        """
        Agrega una sección al documento.
        
        Args:
            section: La sección a agregar
            
        Raises:
            ValueError: Si el documento ya fue generado
        """
        if self._is_generated:
            raise ValueError("No se pueden agregar secciones a un documento generado")
        self.sections.append(section)
    
    def add_table(self, table: PDFTable, section_index: int | None = None) -> None:
        """
        Agrega una tabla al documento.
        
        Args:
            table: La tabla a agregar
            section_index: Índice de la sección donde agregar la tabla.
                          Si es None, se agrega como nueva sección.
        """
        if self._is_generated:
            raise ValueError("No se pueden agregar tablas a un documento generado")
        
        if section_index is not None:
            if section_index < 0 or section_index >= len(self.sections):
                raise IndexError("Índice de sección fuera de rango")
            self.sections[section_index].elements.append(table)
        else:
            # Crear una nueva sección para la tabla
            section = PDFSection(
                title=table.title or "Tabla",
                elements=[table]
            )
            self.sections.append(section)
    
    def mark_as_generated(self) -> None:
        """Marca el documento como generado (inmutable)."""
        self._is_generated = True
    
    @property
    def is_generated(self) -> bool:
        """Indica si el documento ya fue generado."""
        return self._is_generated
    
    @property
    def section_count(self) -> int:
        """Retorna el número de secciones."""
        return len(self.sections)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convierte la entidad a un diccionario.
        
        Útil para serialización y debugging.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "page_size": self.page_size.value,
            "orientation": self.orientation.value,
            "section_count": self.section_count,
            "metadata": self.metadata,
        }
