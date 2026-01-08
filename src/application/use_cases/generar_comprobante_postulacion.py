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
        """Construye el PDFDocument con estructura narrativa profesional."""
        import os
        
        # Obtener ruta del logo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "utils", "images", "logoUTN.png")
        
        document = PDFDocument(
            title=f"Comprobante de Postulación N° {comprobante.postulacion.numero}",
            author="Sistema de Pasantías",
            page_size="A4",
            orientation="portrait",
            metadata={
                "numero_postulacion": comprobante.postulacion.numero,
                "tipo_documento": "comprobante_postulacion",
                "estudiante_dni": comprobante.estudiante.dni,
                "logo_path": logo_path if os.path.exists(logo_path) else None,
                "universidad_nombre": comprobante.universidad.nombre,
            },
        )
        
        # 1. Sección Header - Universidad
        document.add_section(self._build_header_universidad(comprobante))
        
        # 2. Sección Principal - Tabla compacta con datos clave
        document.add_section(self._build_tabla_datos_clave(comprobante))
        
        # 3. Sección Narrativa - Mensaje descriptivo
        document.add_section(self._build_mensaje_narrativo(comprobante))
        
        # 4. Sección de Firma y Footer
        document.add_section(self._build_seccion_firma(comprobante))
        
        return document
    
    def _build_header_universidad(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye el header con nombre de la universidad."""
        univ = comprobante.universidad
        
        return PDFSection(
            title=univ.nombre, # borre la direccion
            level=1,
        )
    
    def _build_tabla_datos_clave(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye tabla compacta con los datos clave del comprobante."""
        from src.application.utils.date_utils import parse_iso_to_spanish_argentina
        
        est = comprobante.estudiante
        carr = comprobante.carrera
        emp = comprobante.empresa
        proy = comprobante.proyecto
        puesto = comprobante.puesto
        post = comprobante.postulacion
        
        # Formatear fecha de inicio del proyecto
        fecha_inicio = parse_iso_to_spanish_argentina(proy.fecha_inicio) or "No especificada"
        
        # Construir filas de la tabla
        rows = [
            ["Estudiante", f"{est.nombre} {est.apellido}"],
            ["DNI", est.dni],
            ["Carrera", carr.nombre],
            ["Empresa", emp.nombre],
            ["Puesto", puesto.nombre],
            ["Proyecto", f"{proy.nombre} (inicio: {fecha_inicio})"],
            ["Materias aprobadas", str(post.cantidad_materias_aprobadas)],
            ["Materias en condición regular", str(post.cantidad_materias_regulares)],
        ]
        
        # Crear tabla
        tabla = PDFTable(
            headers=["Campo", "Información"],
            rows=rows,
            title=None,  # Sin título, solo la tabla
        )
        
        # Formatear número y fecha de postulación
        fecha_post = parse_iso_to_spanish_argentina(post.fecha)
        
        return PDFSection(
            title=f"COMPROBANTE DE POSTULACIÓN N° {post.numero}",
            content=f"Fecha de postulación: {fecha_post}",
            level=1,
            elements=[tabla],
        )
    
    def _build_mensaje_narrativo(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye el mensaje narrativo explicando la postulación."""
        from src.application.utils.date_utils import parse_iso_to_spanish_argentina
        
        est = comprobante.estudiante
        univ = comprobante.universidad
        carr = comprobante.carrera
        emp = comprobante.empresa
        proy = comprobante.proyecto
        puesto = comprobante.puesto
        post = comprobante.postulacion
        
        # Formatear fechas
        fecha_postulacion = parse_iso_to_spanish_argentina(post.fecha)
        fecha_inicio = parse_iso_to_spanish_argentina(proy.fecha_inicio)
        
        # Construir nombre completo
        nombre_completo = f"{est.nombre} {est.apellido}"
        
        # Construir mensaje principal
        mensaje = (
            f"Por medio del presente se certifica que <b>{nombre_completo}</b>, "
            f"alumno/a de <b>{carr.nombre}</b> de la institución <b>{univ.nombre}</b>, "
            f"con DNI <b>{est.dni}</b>, se postuló para el proyecto "
            f"<b>\"{proy.nombre}\"</b> ofrecido por <b>{emp.nombre}</b> "
            f"para el puesto de <b>{puesto.nombre}</b>."
        )
        
        # Agregar fecha de inicio si está disponible
        if fecha_inicio:
            mensaje += f" El proyecto tiene fecha de inicio estimada: <b>{fecha_inicio}</b>."
        
        # Agregar información académica y de registro
        mensaje += (
            f"\n\n"
            f"Al momento de la postulación, el/la estudiante registra "
            f"<b>{post.cantidad_materias_aprobadas} materias aprobadas</b> y "
            f"<b>{post.cantidad_materias_regulares} materias en condición regular</b>. "
            f"Esta postulación queda registrada bajo el número <b>{post.numero}</b>"
        )
        
        if fecha_postulacion:
            mensaje += f" y fue realizada el <b>{fecha_postulacion}</b>."
        else:
            mensaje += "."
        
        return PDFSection(
            title="",  # Sin título para que fluya con el documento
            content=mensaje,
            level=2,
        )
    
    def _build_seccion_firma(
        self, 
        comprobante: ComprobantePostulacionDTO
    ) -> PDFSection:
        """Construye la sección de firma y footer con información de contacto."""
        univ = comprobante.universidad
        
        # Construir contenido de firma y footer
        contenido = (
            "\n\n"
            "__________________________________\n"
            "Firma del responsable académico / Empresa\n\n"
            "Este comprobante es emitido electrónicamente y puede ser "
            "impreso para presentar en la empresa."
        )
        
        return PDFSection(
            title="",  # Sin título
            content=contenido,
            level=3,
        )
