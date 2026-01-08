"""
Generar Comprobante de Contrato Use Case
==========================================

Use case específico para generar contratos de pasantía.

Este use case conoce la estructura de negocio del contrato y construye
automáticamente el documento PDF con las cláusulas apropiadas.

Estructura del contrato:
- Header con universidad y logo
- Título del contrato
- Tabla con datos clave
- Cláusulas narrativas (PRIMERA a QUINTA)
- Sección de firmas
- Footer con contacto
"""

from dataclasses import dataclass
from typing import BinaryIO
import os

from src.domain.entities import PDFDocument, PDFSection, PDFTable
from src.domain.exceptions import InvalidDocumentError, PDFGenerationError
from src.domain.interfaces import IPDFGenerator
from src.domain.value_objects import PDFStyle
from src.application.dto import ComprobanteContratoDTO


@dataclass
class GenerarContratoResult:
    """
    Resultado de la generación del contrato.
    
    Atributos:
        content: Contenido del PDF en bytes
        filename: Nombre del archivo (contrato_pasantia_{numero}.pdf)
        document_id: ID del documento generado
        numero_contrato: Número del contrato procesado
    """
    content: bytes
    filename: str
    document_id: str
    numero_contrato: int


class GenerarComprobanteContratoUseCase:
    """
    Caso de uso para generar contrato de pasantía.
    
    Este caso de uso:
    1. Recibe ComprobanteContratoDTO con todos los datos
    2. Construye el documento PDF con estructura de contrato formal:
       - Encabezado con universidad
       - Título del contrato
       - Metadatos (número, fecha de emisión)
       - Tabla con datos clave
       - Cláusulas del contrato (PRIMERA a QUINTA)
       - Sección de firmas
       - Footer
    3. Genera el PDF usando IPDFGenerator
    4. Retorna el resultado con nombre apropiado
    
    Ejemplo:
        >>> generator = ReportLabGenerator()
        >>> use_case = GenerarComprobanteContratoUseCase(generator)
        >>> result = use_case.execute(contrato_dto)
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
        comprobante: ComprobanteContratoDTO,
        style: PDFStyle | None = None,
    ) -> GenerarContratoResult:
        """
        Ejecuta el caso de uso para generar el contrato.
        
        Args:
            comprobante: DTO con todos los datos del contrato
            style: Estilos opcionales del PDF
            
        Returns:
            GenerarContratoResult con el PDF generado
            
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
                f"Error al generar el contrato de pasantía: {str(e)}",
                details={
                    "document_id": str(document.id),
                    "numero_contrato": comprobante.contrato.numero,
                },
            )
        
        # 5. Marcar documento como generado
        document.mark_as_generated()
        
        # 6. Retornar resultado
        return GenerarContratoResult(
            content=content,
            filename=f"contrato_pasantia_{comprobante.contrato.numero}.pdf",
            document_id=str(document.id),
            numero_contrato=comprobante.contrato.numero,
        )
    
    def execute_to_stream(
        self,
        comprobante: ComprobanteContratoDTO,
        stream: BinaryIO,
        style: PDFStyle | None = None,
    ) -> str:
        """
        Ejecuta el caso de uso escribiendo el PDF a un stream.
        
        Útil para streaming responses en FastAPI.
        
        Args:
            comprobante: DTO con todos los datos del contrato
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
                f"Error al generar el contrato de pasantía: {str(e)}",
                details={
                    "document_id": str(document.id),
                    "numero_contrato": comprobante.contrato.numero,
                },
            )
        
        document.mark_as_generated()
        return str(document.id)
    
    def _validate_comprobante(self, comprobante: ComprobanteContratoDTO) -> None:
        """Valida que el DTO tenga los datos mínimos requeridos."""
        if not comprobante.estudiante or not comprobante.estudiante.nombre:
            raise InvalidDocumentError(
                "Los datos del estudiante son requeridos",
                details={"field": "estudiante"},
            )
        
        if not comprobante.contrato or not comprobante.contrato.numero:
            raise InvalidDocumentError(
                "Los datos del contrato son requeridos",
                details={"field": "contrato"},
            )
        
        if not comprobante.universidad or not comprobante.universidad.nombre:
            raise InvalidDocumentError(
                "Los datos de la universidad son requeridos",
                details={"field": "universidad"},
            )
    
    def _build_document(self, comprobante: ComprobanteContratoDTO) -> PDFDocument:
        """Construye el PDFDocument con estructura de contrato formal."""
        # Obtener ruta del logo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "utils", "images", "logoUTN.png")
        
        document = PDFDocument(
            title=f"Contrato de Pasantía N° {comprobante.contrato.numero}",
            author="Sistema de Pasantías",
            page_size="A4",
            orientation="portrait",
            metadata={
                "numero_contrato": comprobante.contrato.numero,
                "tipo_documento": "contrato_pasantia",
                "estudiante_dni": comprobante.estudiante.dni,
                "logo_path": logo_path if os.path.exists(logo_path) else None,
                "universidad_nombre": comprobante.universidad.nombre,
            },
        )
        
        # 1. Sección Header - Universidad
        document.add_section(self._build_header_universidad(comprobante))
        
        # 2. Sección Título del Contrato
        document.add_section(self._build_titulo_contrato(comprobante))
        
        # 3. Sección Tabla de Datos Clave
        document.add_section(self._build_tabla_datos_clave(comprobante))
        
        # 4. Cláusulas del Contrato
        document.add_section(self._build_clausula_primera(comprobante))
        document.add_section(self._build_clausula_segunda(comprobante))
        document.add_section(self._build_clausula_tercera(comprobante))
        document.add_section(self._build_clausula_cuarta(comprobante))
        document.add_section(self._build_clausula_quinta(comprobante))
        
        # 5. Sección de Firmas
        document.add_section(self._build_seccion_firmas(comprobante))
        
        return document
    
    def _build_header_universidad(
        self, 
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """Construye el header con nombre de la universidad."""
        univ = comprobante.universidad
        
        # Subtítulo con correo si está disponible
        contenido = univ.correo if univ.correo else ""
        
        return PDFSection(
            title=univ.nombre,
            content=contenido,
            level=1,
        )
    
    def _build_titulo_contrato(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """Construye el título del contrato con metadatos."""
        from src.application.utils.date_utils import parse_iso_to_spanish_argentina
        
        contrato = comprobante.contrato
        postulacion = comprobante.postulacion
        
        fecha_emision = parse_iso_to_spanish_argentina(contrato.fecha_emision)
        
        contenido = (
            f"Nº: <b>{postulacion.numero}</b>\n\n"
            f"Fecha de emisión: <b>{fecha_emision}</b>"
        )
        
        return PDFSection(
            title="<b>CONTRATO DE PASANTÍA</b>",
            content=contenido,
            level=1,
        )
    
    def _build_tabla_datos_clave(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """Construye tabla compacta con los datos clave del contrato."""
        from src.application.utils.date_utils import parse_iso_to_spanish_argentina
        
        est = comprobante.estudiante
        carr = comprobante.carrera
        emp = comprobante.empresa
        proy = comprobante.proyecto
        puesto = comprobante.puesto
        post = comprobante.postulacion
        
        # Formatear fechas del proyecto
        fecha_inicio = parse_iso_to_spanish_argentina(proy.fecha_inicio) or "No especificada"
        fecha_fin = parse_iso_to_spanish_argentina(proy.fecha_fin) or "No especificada"
        
        # Construir filas de la tabla
        rows = [
            ["Estudiante:", f"{est.nombre} {est.apellido}"],
            ["DNI / Email:", f"{est.dni} / {est.email}"],
            ["Carrera:", f"{carr.nombre} ({carr.plan_estudios})"],
            ["Empresa:", f"{emp.nombre}"],
            ["Dirección / Tel:", f"{emp.direccion} / {emp.telefono}"],
            ["Proyecto:", f"{proy.nombre}"],
            ["Periodo del proyecto:", f"{fecha_inicio} — {fecha_fin}"],
            ["Puesto / Horas sem.:", f"{puesto.nombre} / {puesto.horas_dedicadas} hs sem."],
            ["Materias aprobadas / regulares:", f"{post.cantidad_materias_aprobadas} / {post.cantidad_materias_regulares}"],
            ["Estado de la postulación:", f"{post.estado}"],
        ]
        
        # Crear tabla
        tabla = PDFTable(
            headers=["Campo", "Información"],
            rows=rows,
            title=None,
        )
        
        return PDFSection(
            title="",
            content="",
            level=2,
            elements=[tabla],
        )
    
    def _build_clausula_primera(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """PRIMERA: ANTECEDENTES."""
        est = comprobante.estudiante
        carr = comprobante.carrera
        emp = comprobante.empresa
        
        nombre_full = f"{est.nombre} {est.apellido}".strip()
        
        contenido = (
            f"<b>PRIMERA: ANTECEDENTES. -</b>\n\n"
            f"Comparecen a la suscripción del presente Contrato, por una parte la Empresa <b>{emp.nombre}</b>, "
            f"con domicilio en <b>{emp.direccion}</b>, representada para estos actos por su representante legal, "
            f"y por otra parte, el/la estudiante <b>{nombre_full}</b>, DNI <b>{est.dni}</b>, "
            f"alumno/a de la carrera <b>{carr.nombre}</b>, "
            f"quien se presenta voluntariamente para realizar las prácticas previstas en el presente contrato."
        )
        
        return PDFSection(
            title="",
            content=contenido,
            level=2,
        )
    
    def _build_clausula_segunda(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """SEGUNDA: OBJETO."""
        proy = comprobante.proyecto
        puesto = comprobante.puesto
        
        contenido = (
            f"<b>SEGUNDA: OBJETO. -</b>\n\n"
            f"El objeto del presente contrato es que el/la estudiante realice prácticas profesionales en el proyecto "
            f"denominado <b>\"{proy.nombre}\"</b> con funciones de <b>{puesto.nombre}</b>, "
            f"bajo la supervisión y dirección de la Empresa. "
            f"Las tareas estarán relacionadas con la formación académica del/la estudiante y con las necesidades del proyecto."
        )
        
        return PDFSection(
            title="",
            content=contenido,
            level=2,
        )
    
    def _build_clausula_tercera(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """TERCERA: LUGAR DE PRÁCTICAS Y HORARIO."""
        emp = comprobante.empresa
        puesto = comprobante.puesto
        
        contenido = (
            f"<b>TERCERA: LUGAR DE PRÁCTICAS Y HORARIO. -</b>\n\n"
            f"Las prácticas se desarrollarán en las oficinas de la Empresa ubicadas en <b>{emp.direccion}</b> "
            f"y/o en modalidad remota según lo acuerden las partes. "
            f"El/la estudiante dedicará aproximadamente <b>{puesto.horas_dedicadas} horas semanales</b>, "
            f"en jornadas compatibles con sus obligaciones académicas."
        )
        
        return PDFSection(
            title="",
            content=contenido,
            level=2,
        )
    
    def _build_clausula_cuarta(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """CUARTA: PENSIÓN / REMUNERACIÓN."""
        contenido = (
            f"<b>CUARTA: PENSIÓN / REMUNERACIÓN. -</b>\n\n"
            f"Las partes acuerdan que la pasantía será no remunerada. "
            f"En caso de corresponder, la determinación y forma de pago se registrará en anexo aparte. "
            f"El/la estudiante conservará los derechos y beneficios de orden legal que correspondan."
        )
        
        return PDFSection(
            title="",
            content=contenido,
            level=2,
        )
    
    def _build_clausula_quinta(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """QUINTA: DURACIÓN."""
        from src.application.utils.date_utils import parse_iso_to_spanish_argentina
        
        contrato = comprobante.contrato
        
        fecha_ini = parse_iso_to_spanish_argentina(contrato.fecha_inicio)
        fecha_fin = parse_iso_to_spanish_argentina(contrato.fecha_fin)
        
        contenido = (
            f"<b>QUINTA: DURACIÓN. -</b>\n\n"
            f"El presente contrato tendrá vigencia desde <b>{fecha_ini}</b> hasta <b>{fecha_fin}</b>, "
            f"sin perjuicio de su prórroga por acuerdo expreso de las partes."
        )
        
        return PDFSection(
            title="",
            content=contenido,
            level=2,
        )
    
    def _build_seccion_firmas(
        self,
        comprobante: ComprobanteContratoDTO
    ) -> PDFSection:
        """Construye la sección de firmas."""
        est = comprobante.estudiante
        emp = comprobante.empresa
        univ = comprobante.universidad
        
        nombre_full = f"{est.nombre} {est.apellido}".strip()
        contacto_uni = univ.correo or ""
        
        contenido = (
            "\n\n"
            "______________________________          ______________________________\n\n"
            f"Firma y sello - {emp.nombre}            Firma del/de la estudiante: {nombre_full}\n\n"
        )
        
        if contacto_uni:
            contenido += f"Contacto prácticas: {contacto_uni}"
        
        return PDFSection(
            title="",
            content=contenido,
            level=3,
        )
