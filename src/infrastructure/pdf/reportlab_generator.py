"""
ReportLab PDF Generator
=======================

Implementación concreta del generador de PDF usando ReportLab.

Esta clase es un "Adapter" que implementa el "Port" definido
en el dominio (IPDFGenerator). Esto permite:
- Intercambiar la implementación sin tocar el dominio
- Testear el dominio con mocks
- Mantener ReportLab aislado en la infraestructura

Decisiones técnicas:
- Se usa ReportLab's Platypus para layout de alto nivel
- Los estilos del dominio se mapean a estilos de ReportLab
- El PDF se genera en memoria (BytesIO) para eficiencia
"""

from io import BytesIO
from typing import BinaryIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from src.domain.entities import PDFDocument, PDFSection, PDFTable
from src.domain.entities.pdf_document import PageSize, PageOrientation
from src.domain.exceptions import PDFGenerationError
from src.domain.interfaces import IPDFGenerator
from src.domain.value_objects import PDFStyle


class ReportLabGenerator(IPDFGenerator):
    """
    Generador de PDF usando ReportLab.
    
    Esta clase implementa la interfaz IPDFGenerator del dominio,
    proporcionando la implementación concreta con ReportLab.
    
    ReportLab es una librería Python para generación de PDFs que:
    - No requiere dependencias externas de sistema
    - Ofrece control pixel-perfect del documento
    - Soporta gráficos, tablas, y layouts complejos
    - Es ideal para generación programática (sin HTML/CSS)
    
    Ejemplo:
        >>> generator = ReportLabGenerator()
        >>> pdf_bytes = generator.generate(document, style)
    """
    
    # Mapeo de tamaños de página del dominio a ReportLab
    PAGE_SIZES = {
        PageSize.A4: A4,
        PageSize.LETTER: LETTER,
        PageSize.LEGAL: LEGAL,
        PageSize.A3: A3,
        PageSize.A5: A5,
    }
    
    def generate(
        self, 
        document: PDFDocument, 
        style: PDFStyle | None = None
    ) -> bytes:
        """
        Genera un PDF y retorna los bytes.
        
        Args:
            document: Documento del dominio a convertir
            style: Estilos opcionales
            
        Returns:
            Contenido del PDF como bytes
        """
        buffer = BytesIO()
        self.generate_to_stream(document, buffer, style)
        buffer.seek(0)
        return buffer.read()
    
    def generate_to_file(
        self,
        document: PDFDocument,
        output_path: str,
        style: PDFStyle | None = None,
    ) -> str:
        """
        Genera un PDF y lo guarda en un archivo.
        
        Args:
            document: Documento del dominio
            output_path: Ruta del archivo de salida
            style: Estilos opcionales
            
        Returns:
            Ruta del archivo generado
        """
        try:
            with open(output_path, "wb") as f:
                self.generate_to_stream(document, f, style)
            return output_path
        except IOError as e:
            raise PDFGenerationError(
                f"Error al escribir el archivo: {str(e)}",
                details={"path": output_path},
            )
    
    def generate_to_stream(
        self,
        document: PDFDocument,
        stream: BinaryIO,
        style: PDFStyle | None = None,
    ) -> None:
        """
        Genera un PDF y lo escribe en un stream.
        
        Este es el método principal que hace el trabajo real.
        Los otros métodos son wrappers alrededor de este.
        
        Args:
            document: Documento del dominio
            stream: Stream binario de salida
            style: Estilos opcionales
        """
        style = style or PDFStyle.default()
        
        try:
            # Obtener tamaño de página
            page_size = self._get_page_size(document)
            
            # Márgenes profesionales más amplios
            from reportlab.lib.units import mm
            top_margin = 32 * mm  # Mayor espacio para header con logo
            bottom_margin = 22 * mm
            left_margin = 22 * mm
            right_margin = 22 * mm
            
            # Crear el documento de ReportLab
            doc = SimpleDocTemplate(
                stream,
                pagesize=page_size,
                topMargin=top_margin,
                bottomMargin=bottom_margin,
                leftMargin=left_margin,
                rightMargin=right_margin,
                title=document.title,
                author=document.author,
            )
            
            # Construir los elementos del documento
            elements = self._build_elements(document, style)
            
            # Detectar si hay logo en metadata para usar callbacks de header/footer
            logo_path = document.metadata.get("logo_path")
            universidad_nombre = document.metadata.get("universidad_nombre")
            
            # Generar el PDF (con o sin header/footer personalizado)
            if logo_path and universidad_nombre:
                # Usar callbacks para header/footer con logo
                doc.build(
                    elements,
                    onFirstPage=lambda c, d: self._draw_header_footer(
                        c, d, logo_path, universidad_nombre
                    ),
                    onLaterPages=lambda c, d: self._draw_header_footer(
                        c, d, logo_path, universidad_nombre
                    ),
                )
            else:
                # Sin header/footer personalizado
                doc.build(elements)
            
        except Exception as e:
            raise PDFGenerationError(
                f"Error al generar el PDF: {str(e)}",
                details={"document_id": str(document.id)},
            )
    
    def _get_page_size(self, document: PDFDocument) -> tuple:
        """Obtiene el tamaño de página de ReportLab."""
        base_size = self.PAGE_SIZES.get(document.page_size, A4)
        
        if document.orientation == PageOrientation.LANDSCAPE:
            return landscape(base_size)
        return base_size
    
    def _build_elements(
        self, 
        document: PDFDocument, 
        style: PDFStyle
    ) -> list:
        """
        Construye la lista de elementos Platypus del documento.
        
        Platypus es el sistema de layout de alto nivel de ReportLab.
        Los elementos se procesan secuencialmente para generar el PDF.
        """
        elements = []
        styles = self._create_styles(style)
        
        # Título del documento
        title = Paragraph(document.title, styles["title"])
        elements.append(title)
        elements.append(Spacer(1, 0.25 * inch))
        
        # Procesar cada sección
        for section in document.sections:
            section_elements = self._build_section(section, styles)
            elements.extend(section_elements)
        
        return elements
    
    def _create_styles(self, style: PDFStyle) -> dict:
        """
        Crea los estilos de Paragraph con tipografía profesional.
        
        Usa Times-Roman/Times-Bold para un look más formal y profesional.
        """
        base_styles = getSampleStyleSheet()
        
        # Color primario como RGB
        primary_rgb = style.colors.to_rgb("primary")
        text_rgb = style.colors.to_rgb("text")
        
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        
        return {
            "title": ParagraphStyle(
                "CustomTitle",
                parent=base_styles["Heading1"],
                fontName="Times-Bold",
                fontSize=14,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=6,
                leading=17,
            ),
            "heading": ParagraphStyle(
                "CustomHeading",
                parent=base_styles["Heading2"],
                fontName="Times-Bold",
                fontSize=10,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceBefore=8,
                spaceAfter=4,
                leading=12,
            ),
            "body": ParagraphStyle(
                "CustomBody",
                parent=base_styles["Normal"],
                fontName="Times-Roman",
                fontSize=10,
                textColor=colors.black,
                leading=14,
                alignment=TA_JUSTIFY,  # Justificado para cláusulas
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=base_styles["Normal"],
                fontName="Times-Roman",
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=8,
                leading=11,
            ),
            "footer": ParagraphStyle(
                "Footer",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_LEFT,
                leading=10,
            ),
        }
    
    def _build_section(self, section: PDFSection, styles: dict) -> list:
        """Construye los elementos de una sección."""
        elements = []
        
        # Título de la sección según nivel
        if section.title:
            if section.level == 1:
                # Nivel 1: Título principal (centrado)
                heading = Paragraph(section.title, styles["title"])
            elif section.level == 3:
                # Nivel 3: Footer (alineado a derecha)
                heading = Paragraph(section.title, styles["footer"])
            else:
                # Nivel 2: Subtítulos
                heading = Paragraph(section.title, styles["heading"])
            elements.append(heading)
        
        # Contenido de texto
        if section.content:
            # Detectar si es contenido de footer/firma por nivel
            if section.level == 3:
                style_to_use = styles["footer"]
            elif section.level == 1 and not section.title:
                # Contenido sin título en nivel 1 = subtítulo
                style_to_use = styles["subtitle"]
            else:
                style_to_use = styles["body"]
            
            # Dividir en párrafos
            paragraphs = section.content.split("\n\n")
            for para_text in paragraphs:
                if para_text.strip():
                    para = Paragraph(para_text.strip(), style_to_use)
                    elements.append(para)
                    elements.append(Spacer(1, 6))
        
        # Procesar elementos (tablas, etc.)
        for element in section.elements:
            if isinstance(element, PDFTable):
                table_elements = self._build_table(element, styles)
                elements.extend(table_elements)
        
        elements.append(Spacer(1, 12))
        return elements
    
    def _build_table(self, table: PDFTable, styles: dict) -> list:
        """Construye una tabla de ReportLab con estilo profesional."""
        from reportlab.lib.units import mm
        
        elements = []
        
        # Título de la tabla (si existe)
        if table.title:
            title = Paragraph(table.title, styles["heading"])
            elements.append(title)
            elements.append(Spacer(1, 4))
        
        # Datos de la tabla
        data = [table.headers] + table.rows
        
        # Anchos de columna profesionales (ajustados según tipo de documento)
        # Para contratos: 45mm etiqueta, 110mm valor
        # Para comprobantes: 48mm etiqueta, 110mm valor
        col_widths = [45*mm, 110*mm] if len(table.headers) == 2 else None
        reportlab_table = Table(data, colWidths=col_widths, hAlign='LEFT')
        
        # Estilo profesional: líneas sutiles, sin fondo en header
        table_style = TableStyle([
            # Tipografía
            ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            
            # Alineación
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            
            # Líneas sutiles con whitesmoke
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.whitesmoke),
            
            # Padding reducido para look más compacto
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
        
        reportlab_table.setStyle(table_style)
        elements.append(reportlab_table)
        elements.append(Spacer(1, 8))
        
        return elements
    
    def _draw_header_footer(
        self,
        canvas,
        doc,
        logo_path: str,
        universidad_nombre: str,
    ) -> None:
        """
        Dibuja header profesional con logo y footer con número de página.
        
        Diseño profesional:
        - Logo UTN en esquina superior izquierda
        - Nombre de universidad centrado
        - Línea gris sutil horizontal
        - Número de página en footer derecho
        
        Args:
            canvas: Canvas de ReportLab para dibujar
            doc: Documento SimpleDocTemplate
            logo_path: Ruta al archivo del logo
            universidad_nombre: Nombre de la universidad para el header
        """
        from reportlab.lib.units import mm
        import os
        
        width, height = A4
        margin_left = doc.leftMargin
        margin_right = doc.rightMargin
        
        # Dibuja logo UTN en la esquina superior IZQUIERDA
        if logo_path and os.path.exists(logo_path):
            try:
                logo_w = 42 * mm
                logo_h = 14 * mm
                x_logo = margin_left
                y_logo = height - doc.topMargin + 6 * mm
                canvas.drawImage(
                    logo_path,
                    x_logo, y_logo,
                    width=logo_w,
                    height=logo_h,
                    preserveAspectRatio=True,
                    anchor='nw'
                )
            except Exception:
                # Si falla cargar el logo, continuar sin él
                pass
        
        # Universidad nombre CENTRADO (discreto, profesional)
        canvas.setFont("Times-Bold", 9)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(width / 2.0, height - doc.topMargin + 10, universidad_nombre or "")
        
        # Línea horizontal sutil bajo header
        canvas.setStrokeColor(colors.lightgrey)
        canvas.setLineWidth(0.4)  # Más delgada que antes (era 0.5)
        canvas.line(
            margin_left,
            height - doc.topMargin + 4,
            width - margin_right,
            height - doc.topMargin + 4
        )
        
        # Footer: número de página (derecha, discreto)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            width - margin_right,
            doc.bottomMargin - 8,
            f"Página {doc.page}"
        )
