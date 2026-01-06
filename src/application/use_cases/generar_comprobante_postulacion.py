"""
Generar Comprobante de Postulación Use Case
============================================

Use case específico para generar comprobantes de postulación a pasantías.

Este use case conoce la estructura de negocio del comprobante y construye
automáticamente el documento PDF con las secciones apropiadas.

Diferencias con GeneratePDFUseCase:
- GeneratePDFUseCase: Genérico, recibe estructura libre de secciones
- Este use case: Específico, conoce el dominio de postulaciones
"""

from dataclasses import dataclass
from typing import BinaryIO

from src.domain.entities import PDFDocument, PDFSection, PDFTable
from src.domain.exceptions import InvalidDocumentError, PDFGenerationError
from src.domain.interfaces import IPDFGenerator
from src.domain.value_objects import PDFStyle
from src.application.dto import ComprobantePostulacionDTO


@dataclass
class GenerarComprobanteResult:
    """
    Resultado de la generación del comprobante de postulación.
    
    Atributos:
        content: Contenido del PDF en bytes
        filename: Nombre del archivo (comprobante_postulacion_{numero}.pdf)
        document_id: ID del documento generado
        numero_postulacion: Número de la postulación procesada
    """
    content: bytes
    filename: str
    document_id: str
    numero_postulacion: int


class GenerarComprobantePostulacionUseCase:
    """
    Caso de uso para generar comprobante de postulación.
    
    Este caso de uso:
    1. Recibe ComprobantePostulacionDTO con todos los datos
    2. Construye el documento PDF con estructura específica:
       - Encabezado con título del comprobante
       - Sección de datos del estudiante
       - Sección de datos académicos (universidad y carrera)
       - Sección de datos de la postulación (empresa, proyecto, puesto)
       - Sección de estado de la postulación
    3. Genera el PDF usando IPDFGenerator
    4. Retorna el resultado con nombre apropiado
    
    Ejemplo:
        >>> generator = ReportLabGenerator()
        >>> use_case = GenerarComprobantePostulacionUseCase(generator)
        >>> result = use_case.execute(comprobante_dto)
        >>> pdf_bytes = result.content
    """
    
    def __init__(self, pdf_generator: IPDFGenerator) -> None:
        """
        Inicializa el caso de uso.
        
        Args:
            pdf_generator: Implementación del generador de PDF
        """
        self._generator = pdf_generator
    
    def execute(
        self,
        comprobante: ComprobantePostulacionDTO,
        style: PDFStyle | None = None,
    ) -> GenerarComprobanteResult:
        """
        Ejecuta el caso de uso para generar el comprobante.
        
        Args:
            comprobante: DTO con todos los datos del comprobante
            style: Estilos opcionales del PDF
            
        Returns:
            GenerarComprobanteResult con el PDF generado
            
        Raises:
            InvalidDocumentError: Si los datos son inválidos
            PDFGenerationError: Si falla la generación
        """
        # 1. Validar datos de entrada
        self._validate_comprobante(comprobante)
        
        # 2. Construir el documento PDF
        document = self._build_document(comprobante)
        
        # 3. Usar estilo predeterminado si no se proporciona
        pdf_style = style or PDFStyle.default()
        
        # 4. Generar el PDF
        try:
            content = self._generator.generate(document, pdf_style)
        except Exception as e:
            raise PDFGenerationError(
                f"Error al generar el comprobante de postulación: {str(e)}",
                details={
                    "document_id": str(document.id),
                    "numero_postulacion": comprobante.postulacion.numero,
                },
            )
        
        # 5. Marcar documento como generado
        document.mark_as_generated()
        
        # 6. Retornar resultado
        return GenerarComprobanteResult(
            content=content,
            filename=f"comprobante_postulacion_{comprobante.postulacion.numero}.pdf",
            document_id=str(document.id),
            numero_postulacion=comprobante.postulacion.numero,
        )
    
    def execute_to_stream(
        self,
        comprobante: ComprobantePostulacionDTO,
        stream: BinaryIO,
        style: PDFStyle | None = None,
    ) -> str:
        """
        Ejecuta el caso de uso escribiendo el PDF a un stream.
        
        Útil para streaming responses en FastAPI.
        
        Args:
            comprobante: DTO con todos los datos del comprobante
            stream: Stream donde escribir el PDF
            style: Estilos opcionales del PDF
            
        Returns:
            El ID del documento generado
        """
        self._validate_comprobante(comprobante)
        document = self._build_document(comprobante)
        pdf_style = style or PDFStyle.default()
        
        try:
            self._generator.generate_to_stream(document, stream, pdf_style)
        except Exception as e:
            raise PDFGenerationError(
                f"Error al generar el comprobante de postulación: {str(e)}",
                details={
                    "document_id": str(document.id),
                    "numero_postulacion": comprobante.postulacion.numero,
                },
            )
        
        document.mark_as_generated()
        return str(document.id)
    
    def _validate_comprobante(self, comprobante: ComprobantePostulacionDTO) -> None:
        """Valida que el DTO tenga los datos mínimos requeridos."""
        if not comprobante.estudiante or not comprobante.estudiante.nombre:
            raise InvalidDocumentError(
                "Los datos del estudiante son requeridos",
                details={"field": "estudiante"},
            )
        
        if not comprobante.postulacion or not comprobante.postulacion.numero:
            raise InvalidDocumentError(
                "Los datos de la postulación son requeridos",
                details={"field": "postulacion"},
            )
        
        if not comprobante.universidad or not comprobante.universidad.nombre:
            raise InvalidDocumentError(
                "Los datos de la universidad son requeridos",
                details={"field": "universidad"},
            )
    
    def _build_document(self, comprobante: ComprobantePostulacionDTO) -> PDFDocument:
        """Construye el PDFDocument con la estructura del comprobante."""
        document = PDFDocument(
            title=f"Comprobante de Postulación N° {comprobante.postulacion.numero}",
            author="Sistema de Pasantías",
            page_size="A4",
            orientation="portrait",
            metadata={
                "numero_postulacion": comprobante.postulacion.numero,
                "tipo_documento": "comprobante_postulacion",
                "estudiante_dni": comprobante.estudiante.dni,
            },
        )
        
        # Sección 1: Datos del Estudiante
        document.add_section(self._build_seccion_estudiante(comprobante))
        
        # Sección 2: Datos Académicos (Universidad y Carrera)
        document.add_section(self._build_seccion_academica(comprobante))
        
        # Sección 3: Datos de la Postulación (Empresa, Proyecto, Puesto)
        document.add_section(self._build_seccion_postulacion_detalles(comprobante))
        
        # Sección 4: Estado de la Postulación
        document.add_section(self._build_seccion_estado(comprobante))
        
        return document
    
    def _build_seccion_estudiante(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye la sección con datos del estudiante."""
        est = comprobante.estudiante
        
        section = PDFSection(
            title="Datos del Estudiante",
            level=1,
        )
        
        # Tabla con datos del estudiante
        tabla = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Nombre Completo", f"{est.apellido}, {est.nombre}"],
                ["DNI", est.dni],
                ["CUIL", est.cuil],
                ["Tipo de Documento", est.tipo_dni],
                ["Email", est.email],
                ["Fecha de Nacimiento", est.fecha_nacimiento or "No especificada"],
            ],
            title="Información Personal",
        )
        
        section.elements.append(tabla)
        return section
    
    def _build_seccion_academica(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye la sección con datos académicos."""
        univ = comprobante.universidad
        carr = comprobante.carrera
        
        section = PDFSection(
            title="Datos Académicos",
            level=1,
        )
        
        # Tabla con datos de la universidad
        tabla_universidad = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Universidad", univ.nombre],
                ["Dirección", univ.direccion],
                ["Código Postal", str(univ.codigo_postal)],
                ["Email", univ.correo or "No especificado"],
                ["Teléfono", univ.telefono or "No especificado"],
            ],
            title="Institución Educativa",
        )
        
        # Tabla con datos de la carrera
        tabla_carrera = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Carrera", carr.nombre],
                ["Código", carr.codigo],
                ["Descripción", carr.descripcion or "No especificada"],
                ["Plan de Estudios", carr.plan_estudios or "No especificado"],
            ],
            title="Carrera",
        )
        
        section.elements.append(tabla_universidad)
        section.elements.append(tabla_carrera)
        return section
    
    def _build_seccion_postulacion_detalles(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye la sección con detalles de la postulación."""
        emp = comprobante.empresa
        proy = comprobante.proyecto
        puesto = comprobante.puesto
        
        section = PDFSection(
            title="Detalles de la Postulación",
            level=1,
        )
        
        # Tabla con datos de la empresa
        tabla_empresa = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Empresa", emp.nombre],
                ["Código Empresa", str(emp.codigo) if emp.codigo else "No especificado"],
                ["Dirección", emp.direccion],
                ["Código Postal", str(emp.codigo_postal)],
                ["Teléfono", emp.telefono or "No especificado"],
            ],
            title="Empresa Oferente",
        )
        
        # Tabla con datos del proyecto
        tabla_proyecto = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Proyecto", proy.nombre],
                ["Número", str(proy.numero)],
                ["Descripción", proy.descripcion],
                ["Estado", proy.estado or "No especificado"],
                ["Fecha Inicio", proy.fecha_inicio or "No especificada"],
                ["Fecha Fin", proy.fecha_fin or "No especificada"],
            ],
            title="Proyecto de Pasantía",
        )
        
        # Tabla con datos del puesto
        tabla_puesto = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Puesto", puesto.nombre],
                ["Código", str(puesto.codigo) if puesto.codigo else "No especificado"],
                ["Descripción", puesto.descripcion],
                ["Horas Semanales", f"{puesto.horas_dedicadas} hs"],
            ],
            title="Puesto Solicitado",
        )
        
        section.elements.append(tabla_empresa)
        section.elements.append(tabla_proyecto)
        section.elements.append(tabla_puesto)
        return section
    
    def _build_seccion_estado(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye la sección con el estado de la postulación."""
        post = comprobante.postulacion
        
        section = PDFSection(
            title="Estado de la Postulación",
            level=1,
        )
        
        # Tabla con estado de la postulación
        tabla = PDFTable(
            headers=["Campo", "Valor"],
            rows=[
                ["Número de Postulación", str(post.numero)],
                ["Fecha de Postulación", post.fecha],
                ["Estado", post.estado],
                ["Materias Aprobadas", str(post.cantidad_materias_aprobadas)],
                ["Materias Regulares", str(post.cantidad_materias_regulares)],
            ],
            title="Información de la Postulación",
        )
        
        section.elements.append(tabla)
        return section
