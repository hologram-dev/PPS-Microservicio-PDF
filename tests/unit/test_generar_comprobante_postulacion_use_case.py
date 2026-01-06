"""
Tests Unitarios - Use Case Generar Comprobante de Postulación
==============================================================

Tests para el use case de generación de comprobantes de postulación.
"""

import pytest
from unittest.mock import Mock, MagicMock
from io import BytesIO

from src.application.use_cases.generar_comprobante_postulacion import (
    GenerarComprobantePostulacionUseCase,
    GenerarComprobanteResult,
)
from src.domain.exceptions import InvalidDocumentError, PDFGenerationError
from src.domain.interfaces import IPDFGenerator
from src.domain.value_objects import PDFStyle

# Importar mocks
import sys
from pathlib import Path
tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tests_dir))

from test_data.comprobante_postulacion_mocks import (
    mock_comprobante_postulacion_dto,
    mock_comprobante_minimo,
)


@pytest.fixture
def mock_pdf_generator():
    """Fixture que crea un mock del generador de PDF."""
    generator = Mock(spec=IPDFGenerator)
    generator.generate.return_value = b"PDF_CONTENT_MOCK"
    generator.generate_to_stream.return_value = None
    return generator


@pytest.fixture
def use_case(mock_pdf_generator):
    """Fixture que crea una instancia del use case con generador mock."""
    return GenerarComprobantePostulacionUseCase(mock_pdf_generator)


# ================================
# Tests de Generación Exitosa
# ================================

def test_generate_comprobante_exitoso(use_case, mock_pdf_generator):
    """Test de generación exitosa de comprobante."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    
    # Act
    result = use_case.execute(comprobante_dto)
    
    # Assert
    assert isinstance(result, GenerarComprobanteResult)
    assert result.content == b"PDF_CONTENT_MOCK"
    assert result.filename == "comprobante_postulacion_5432.pdf"
    assert result.numero_postulacion == 5432
    assert result.document_id is not None
    
    # Verificar que se llamó al generador
    mock_pdf_generator.generate.assert_called_once()


def test_generate_comprobante_con_datos_minimos(use_case, mock_pdf_generator):
    """Test de generación con datos mínimos."""
    # Arrange
    comprobante_dto = mock_comprobante_minimo()
    
    # Act
    result = use_case.execute(comprobante_dto)
    
    # Assert
    assert isinstance(result, GenerarComprobanteResult)
    assert result.filename == "comprobante_postulacion_9999.pdf"
    assert result.numero_postulacion == 9999


def test_generate_comprobante_con_estilo_custom(use_case, mock_pdf_generator):
    """Test de generación con estilo personalizado."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    custom_style = PDFStyle.default()
    
    # Act
    result = use_case.execute(comprobante_dto, style=custom_style)
    
    # Assert
    assert isinstance(result, GenerarComprobanteResult)
    mock_pdf_generator.generate.assert_called_once()


def test_generate_comprobante_filename_correcto(use_case):
    """Test que verifica el formato correcto del filename."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    
    # Act
    result = use_case.execute(comprobante_dto)
    
    # Assert
    assert result.filename.startswith("comprobante_postulacion_")
    assert result.filename.endswith(".pdf")
    assert "5432" in result.filename


# ================================
# Tests de Validación
# ================================

def test_generate_comprobante_sin_estudiante(use_case):
    """Test que rechaza comprobante sin datos de estudiante."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    comprobante_dto.estudiante = None
    
    # Act & Assert
    with pytest.raises(InvalidDocumentError) as exc_info:
        use_case.execute(comprobante_dto)
    
    assert "estudiante" in str(exc_info.value).lower()


def test_generate_comprobante_sin_postulacion(use_case):
    """Test que rechaza comprobante sin datos de postulación."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    comprobante_dto.postulacion = None
    
    # Act & Assert
    with pytest.raises(InvalidDocumentError) as exc_info:
        use_case.execute(comprobante_dto)
    
    # Verificar que el mensaje de error menciona postulación
    assert "postulaci" in str(exc_info.value).lower() or "requeridos" in str(exc_info.value).lower()


def test_generate_comprobante_sin_universidad(use_case):
    """Test que rechaza comprobante sin datos de universidad."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    comprobante_dto.universidad = None
    
    # Act & Assert
    with pytest.raises(InvalidDocumentError) as exc_info:
        use_case.execute(comprobante_dto)
    
    assert "universidad" in str(exc_info.value).lower()


# ================================
# Tests de Manejo de Errores
# ================================

def test_generate_comprobante_error_en_generador(use_case, mock_pdf_generator):
    """Test que maneja errores del generador de PDF."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    mock_pdf_generator.generate.side_effect = Exception("Error de ReportLab")
    
    # Act & Assert
    with pytest.raises(PDFGenerationError) as exc_info:
        use_case.execute(comprobante_dto)
    
    assert "Error al generar el comprobante" in str(exc_info.value)
    assert "5432" in str(exc_info.value.details.get("numero_postulacion", ""))


# ================================
# Tests de execute_to_stream
# ================================

def test_generate_to_stream_exitoso(use_case, mock_pdf_generator):
    """Test de generación a stream."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    stream = BytesIO()
    
    # Act
    document_id = use_case.execute_to_stream(comprobante_dto, stream)
    
    # Assert
    assert document_id is not None
    assert isinstance(document_id, str)
    mock_pdf_generator.generate_to_stream.assert_called_once()


def test_generate_to_stream_con_estilo(use_case, mock_pdf_generator):
    """Test de generación a stream con estilo."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    stream = BytesIO()
    custom_style = PDFStyle.default()
    
    # Act
    document_id = use_case.execute_to_stream(comprobante_dto, stream, style=custom_style)
    
    # Assert
    assert document_id is not None
    mock_pdf_generator.generate_to_stream.assert_called_once()


def test_generate_to_stream_error_en_generador(use_case, mock_pdf_generator):
    """Test que maneja errores al escribir a stream."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    stream = BytesIO()
    mock_pdf_generator.generate_to_stream.side_effect = Exception("Stream error")
    
    # Act & Assert
    with pytest.raises(PDFGenerationError):
        use_case.execute_to_stream(comprobante_dto, stream)


# ================================
# Tests de Construcción del Documento
# ================================

def test_document_contiene_titulo_correcto(use_case, mock_pdf_generator):
    """Test que verifica que el documento tiene el título correcto."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    
    # Capturar el documento pasado al generador
    captured_document = None
    def capture_document(document, style):
        nonlocal captured_document
        captured_document = document
        return b"PDF_MOCK"
    
    mock_pdf_generator.generate.side_effect = capture_document
    
    # Act
    use_case.execute(comprobante_dto)
    
    # Assert
    assert captured_document is not None
    assert "5432" in captured_document.title
    assert "Comprobante de Postulación" in captured_document.title


def test_document_contiene_cuatro_secciones(use_case, mock_pdf_generator):
    """Test que verifica que el documento tiene las 4 secciones esperadas."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    
    # Capturar el documento
    captured_document = None
    def capture_document(document, style):
        nonlocal captured_document
        captured_document = document
        return b"PDF_MOCK"
    
    mock_pdf_generator.generate.side_effect = capture_document
    
    # Act
    use_case.execute(comprobante_dto)
    
    # Assert
    assert captured_document is not None
    assert len(captured_document.sections) == 4
    
    # Verificar nombres de secciones
    section_titles = [s.title for s in captured_document.sections]
    assert "Datos del Estudiante" in section_titles
    assert "Datos Académicos" in section_titles
    assert "Detalles de la Postulación" in section_titles
    assert "Estado de la Postulación" in section_titles


def test_document_metadata_correcta(use_case, mock_pdf_generator):
    """Test que verifica los metadatos del documento."""
    # Arrange
    comprobante_dto = mock_comprobante_postulacion_dto()
    
    # Capturar el documento
    captured_document = None
    def capture_document(document, style):
        nonlocal captured_document
        captured_document = document
        return b"PDF_MOCK"
    
    mock_pdf_generator.generate.side_effect = capture_document
    
    # Act
    use_case.execute(comprobante_dto)
    
    # Assert
    assert captured_document is not None
    assert captured_document.metadata["numero_postulacion"] == 5432
    assert captured_document.metadata["tipo_documento"] == "comprobante_postulacion"
    assert captured_document.metadata["estudiante_dni"] == "12345678"
