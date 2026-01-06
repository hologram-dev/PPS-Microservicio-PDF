"""
Generate PDF Use Case
=====================

Caso de uso principal para generar documentos PDF.

Los casos de uso en Clean Architecture:
- Representan una única acción del sistema
- Orquestan entidades del dominio
- Usan las interfaces (ports) para operaciones externas
- No conocen la implementación de la infraestructura

Este caso de uso:
1. Recibe datos de entrada (DTO)
2. Crea/valida entidades del dominio
3. Usa el generador de PDF (a través de la interfaz)
4. Retorna el resultado
"""

from dataclasses import dataclass
from typing import BinaryIO

from src.domain.entities import PDFDocument, PDFSection, PDFTable
from src.domain.exceptions import InvalidDocumentError, PDFGenerationError
from src.domain.interfaces import IPDFGenerator
from src.domain.value_objects import PDFStyle, ColorConfig, FontConfig, MarginConfig
from src.application.dto import PDFRequestDTO, PDFSectionDTO, PDFTableDTO, PDFStyleDTO


@dataclass
class GeneratePDFResult:
    """
    Resultado de la generación de PDF.
    
    Atributos:
        content: Contenido del PDF en bytes
        filename: Nombre sugerido para el archivo
        document_id: ID del documento generado
    """
    content: bytes
    filename: str
    document_id: str


class GeneratePDFUseCase:
    """
    Caso de uso para generar un documento PDF.
    
    Este caso de uso:
    1. Valida los datos de entrada
    2. Construye el documento PDF (entidades del dominio)
    3. Aplica los estilos
    4. Genera el PDF usando el generador (interfaz)
    5. Retorna el resultado
    
    Ejemplo:
        >>> generator = ReportLabGenerator()  # De infraestructura
        >>> use_case = GeneratePDFUseCase(generator)
        >>> result = use_case.execute(request_dto)
        >>> pdf_bytes = result.content
    """
    
    def __init__(self, pdf_generator: IPDFGenerator) -> None:
        """
        Inicializa el caso de uso.
        
        Args:
            pdf_generator: Implementación del generador de PDF
                          (inyectada por el contenedor de dependencias)
        """
        self._generator = pdf_generator
    
    def execute(
        self, 
        request: PDFRequestDTO,
        style: PDFStyleDTO | PDFStyle | None = None,
    ) -> GeneratePDFResult:
        """
        Ejecuta el caso de uso.
        
        Args:
            request: DTO con los datos del PDF a generar
            style: Estilos opcionales (puede ser PDFStyleDTO o PDFStyle)
            
        Returns:
            GeneratePDFResult con el PDF generado
            
        Raises:
            InvalidDocumentError: Si los datos son inválidos
            PDFGenerationError: Si falla la generación
        """
        # 1. Validar datos de entrada
        self._validate_request(request)
        
        # 2. Construir el documento del dominio
        document = self._build_document(request)
        
        # 3. Convertir estilo DTO a value object si es necesario
        pdf_style: PDFStyle
        if isinstance(style, PDFStyleDTO):
            pdf_style = self._convert_style_dto(style)
        elif isinstance(style, PDFStyle):
            pdf_style = style
        else:
            pdf_style = PDFStyle.default()
        
        # 4. Generar el PDF usando la interfaz
        try:
            content = self._generator.generate(document, pdf_style)
        except Exception as e:
            raise PDFGenerationError(
                f"Error al generar el PDF: {str(e)}",
                details={"document_id": str(document.id)},
            )
        
        # 5. Marcar el documento como generado
        document.mark_as_generated()
        
        # 6. Retornar resultado
        return GeneratePDFResult(
            content=content,
            filename=self._generate_filename(document),
            document_id=str(document.id),
        )
    
    def execute_to_stream(
        self,
        request: PDFRequestDTO,
        stream: BinaryIO,
        style: PDFStyleDTO | PDFStyle | None = None,
    ) -> str:
        """
        Ejecuta el caso de uso escribiendo a un stream.
        
        Útil para streaming responses.
        
        Args:
            request: DTO con los datos del PDF a generar
            stream: Stream donde escribir el PDF
            style: Estilos opcionales (puede ser PDFStyleDTO o PDFStyle)
            
        Returns:
            El ID del documento generado
        """
        self._validate_request(request)
        document = self._build_document(request)
        
        # Convertir estilo DTO a value object si es necesario
        pdf_style: PDFStyle
        if isinstance(style, PDFStyleDTO):
            pdf_style = self._convert_style_dto(style)
        elif isinstance(style, PDFStyle):
            pdf_style = style
        else:
            pdf_style = PDFStyle.default()
        
        try:
            self._generator.generate_to_stream(document, stream, pdf_style)
        except Exception as e:
            raise PDFGenerationError(
                f"Error al generar el PDF: {str(e)}",
                details={"document_id": str(document.id)},
            )
        
        document.mark_as_generated()
        return str(document.id)
    
    def _validate_request(self, request: PDFRequestDTO) -> None:
        """Valida los datos de entrada."""
        if not request.title or not request.title.strip():
            raise InvalidDocumentError(
                "El título del documento es requerido",
                details={"field": "title"},
            )
        
        if not request.sections:
            raise InvalidDocumentError(
                "El documento debe tener al menos una sección",
                details={"section_count": 0},
            )
    
    def _build_document(self, request: PDFRequestDTO) -> PDFDocument:
        """Construye un PDFDocument a partir del DTO."""
        document = PDFDocument(
            title=request.title,
            author=request.author or "System",
            page_size=request.page_size,
            orientation=request.orientation,
            metadata=request.metadata or {},
        )
        
        # Agregar secciones
        for section_dto in request.sections:
            section = self._build_section(section_dto)
            document.add_section(section)
        
        return document
    
    def _build_section(self, section_dto: PDFSectionDTO) -> PDFSection:
        """Construye una PDFSection a partir del DTO."""
        section = PDFSection(
            title=section_dto.title,
            content=section_dto.content or "",
            level=section_dto.level,
        )
        
        # Agregar tablas si existen
        if section_dto.tables:
            for table_dto in section_dto.tables:
                table = self._build_table(table_dto)
                section.elements.append(table)
        
        return section
    
    def _build_table(self, table_dto: PDFTableDTO) -> PDFTable:
        """Construye una PDFTable a partir del DTO."""
        return PDFTable(
            headers=table_dto.headers,
            rows=table_dto.rows,
            title=table_dto.title,
        )
    
    def _convert_style_dto(self, style_dto: PDFStyleDTO) -> PDFStyle:
        """
        Convierte un StyleDTO a un PDFStyle value object.
        
        Este método mapea los valores simples del DTO
        a los value objects complejos del dominio.
        
        Args:
            style_dto: DTO con estilos
            
        Returns:
            PDFStyle value object del dominio
        """
        # Construir configuración de colores
        color_kwargs = {}
        if style_dto.primary_color:
            color_kwargs["primary"] = style_dto.primary_color
        if style_dto.text_color:
            color_kwargs["text"] = style_dto.text_color
        
        colors = ColorConfig(**color_kwargs) if color_kwargs else ColorConfig()
        
        # Construir configuración de fuentes
        font_kwargs = {}
        if style_dto.font_size:
            font_kwargs["size_body"] = style_dto.font_size
        
        fonts = FontConfig(**font_kwargs) if font_kwargs else FontConfig()
        
        # Construir configuración de márgenes
        margin_kwargs = {}
        if style_dto.margin_top is not None:
            margin_kwargs["top"] = style_dto.margin_top
        if style_dto.margin_bottom is not None:
            margin_kwargs["bottom"] = style_dto.margin_bottom
        if style_dto.margin_left is not None:
            margin_kwargs["left"] = style_dto.margin_left
        if style_dto.margin_right is not None:
            margin_kwargs["right"] = style_dto.margin_right
        
        margins = MarginConfig(**margin_kwargs) if margin_kwargs else MarginConfig()
        
        return PDFStyle(colors=colors, fonts=fonts, margins=margins)
    
    def _generate_filename(self, document: PDFDocument) -> str:
        """Genera un nombre de archivo para el PDF."""
        # Sanitizar el título para usarlo como nombre de archivo
        safe_title = "".join(
            c for c in document.title 
            if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_title = safe_title.replace(" ", "_")
        
        return f"{safe_title}_{document.id}.pdf"
