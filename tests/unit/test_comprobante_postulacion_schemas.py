"""
Tests Unitarios - Schemas de Comprobante de Postulación
========================================================

Tests para validación de schemas Pydantic del comprobante de postulación.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

from src.presentation.schemas.comprobante_postulacion_schemas import (
    EstudianteSchema,
    UniversidadSchema,
    CarreraSchema,
    EmpresaSchema,
    ProyectoSchema,
    PuestoSchema,
    PostulacionSchema,
    ComprobantePostulacionRequest,
)


# ================================
# Tests de EstudianteSchema
# ================================

def test_estudiante_schema_valido():
    """Test de validación exitosa de estudiante."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan.perez@universidad.edu",
        "dni": "12345678",
        "cuil": "20-12345678-9",
        "fecha_nacimiento": "1998-05-15",
        "tipo_dni": "DNI",
    }
    estudiante = EstudianteSchema(**data)
    
    assert estudiante.nombre == "Juan"
    assert estudiante.apellido == "Pérez"
    assert estudiante.email == "juan.perez@universidad.edu"
    assert estudiante.cuil == "20-12345678-9"


def test_estudiante_schema_email_invalido():
    """Test que rechaza email inválido."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "email-invalido",
        "dni": "12345678",
        "cuil": "20-12345678-9",
    }
    
    with pytest.raises(ValidationError) as exc_info:
        EstudianteSchema(**data)
    
    assert "email" in str(exc_info.value).lower()


def test_estudiante_schema_cuil_invalido():
    """Test que rechaza formato de CUIL inválido."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan@universidad.edu",
        "dni": "12345678",
        "cuil": "20123456789",  # Sin guiones
    }
    
    with pytest.raises(ValidationError) as exc_info:
        EstudianteSchema(**data)
    
    assert "cuil" in str(exc_info.value).lower()


def test_estudiante_schema_fecha_nacimiento_futura():
    """Test que rechaza fecha de nacimiento futura."""
    fecha_futura = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan@universidad.edu",
        "dni": "12345678",
        "cuil": "20-12345678-9",
        "fecha_nacimiento": fecha_futura,
    }
    
    with pytest.raises(ValidationError) as exc_info:
        EstudianteSchema(**data)
    
    assert "futuro" in str(exc_info.value).lower()


def test_estudiante_schema_sin_fecha_nacimiento():
    """Test que acepta fecha de nacimiento opcional."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan@universidad.edu",
        "dni": "12345678",
        "cuil": "20-12345678-9",
    }
    
    estudiante = EstudianteSchema(**data)
    assert estudiante.fecha_nacimiento is None


# ================================
# Tests de UniversidadSchema
# ================================

def test_universidad_schema_valida():
    """Test de validación exitosa de universidad."""
    data = {
        "nombre": "Universidad Nacional",
        "direccion": "Av. Principal 123",
        "codigo_postal": 5000,
        "correo": "contacto@universidad.edu",
        "telefono": "+54 351 1234567",
    }
    
    universidad = UniversidadSchema(**data)
    assert universidad.codigo_postal == 5000


def test_universidad_schema_codigo_postal_invalido():
    """Test que rechaza código postal fuera de rango."""
    data = {
        "nombre": "Universidad Nacional",
        "direccion": "Av. Principal 123",
        "codigo_postal": 999,  # Menor a 1000
    }
    
    with pytest.raises(ValidationError):
        UniversidadSchema(**data)


def test_universidad_schema_campos_opcionales():
    """Test que acepta campos opcionales vacíos."""
    data = {
        "nombre": "Universidad Nacional",
        "direccion": "Av. Principal 123",
        "codigo_postal": 5000,
    }
    
    universidad = UniversidadSchema(**data)
    assert universidad.correo is None
    assert universidad.telefono is None


# ================================
# Tests de ProyectoSchema
# ================================

def test_proyecto_schema_valido():
    """Test de validación exitosa de proyecto."""
    data = {
        "nombre": "Desarrollo Web",
        "descripcion": "Desarrollo de aplicaciones web",
        "numero": 1001,
        "estado": "ACTIVO",
        "fecha_inicio": "2026-02-01",
        "fecha_fin": "2026-08-01",
    }
    
    proyecto = ProyectoSchema(**data)
    assert proyecto.numero == 1001
    assert proyecto.estado == "ACTIVO"


def test_proyecto_schema_fecha_invalida():
    """Test que rechaza formato de fecha inválido."""
    data = {
        "nombre": "Desarrollo Web",
        "descripcion": "Desarrollo de aplicaciones web",
        "numero": 1001,
        "fecha_inicio": "01/02/2026",  # Formato incorrecto
    }
    
    with pytest.raises(ValidationError):
        ProyectoSchema(**data)


# ================================
# Tests de PuestoSchema
# ================================

def test_puesto_schema_valido():
    """Test de validación exitosa de puesto."""
    data = {
        "nombre": "Desarrollador Junior",
        "descripcion": "Desarrollo de aplicaciones",
        "codigo": 501,
        "horas_dedicadas": 20.0,
    }
    
    puesto = PuestoSchema(**data)
    assert puesto.horas_dedicadas == 20.0


def test_puesto_schema_horas_negativas():
    """Test que rechaza horas negativas."""
    data = {
        "nombre": "Desarrollador Junior",
        "descripcion": "Desarrollo de aplicaciones",
        "horas_dedicadas": -5.0,
    }
    
    with pytest.raises(ValidationError):
        PuestoSchema(**data)


def test_puesto_schema_horas_excesivas():
    """Test que rechaza horas excesivas (> 168 horas/semana)."""
    data = {
        "nombre": "Desarrollador Junior",
        "descripcion": "Desarrollo de aplicaciones",
        "horas_dedicadas": 200.0,
    }
    
    with pytest.raises(ValidationError):
        PuestoSchema(**data)


# ================================
# Tests de PostulacionSchema
# ================================

def test_postulacion_schema_valida():
    """Test de validación exitosa de postulación."""
    data = {
        "numero": 5432,
        "fecha": "2026-01-05T10:30:00",
        "estado": "PENDIENTE",
        "cantidad_materias_aprobadas": 25,
        "cantidad_materias_regulares": 30,
    }
    
    postulacion = PostulacionSchema(**data)
    assert postulacion.numero == 5432
    assert postulacion.estado == "PENDIENTE"


def test_postulacion_schema_materias_negativas():
    """Test que rechaza cantidad de materias negativa."""
    data = {
        "numero": 5432,
        "fecha": "2026-01-05T10:30:00",
        "estado": "PENDIENTE",
        "cantidad_materias_aprobadas": -5,
    }
    
    with pytest.raises(ValidationError):
        PostulacionSchema(**data)


# ================================
# Tests de ComprobantePostulacionRequest
# ================================

def test_comprobante_postulacion_request_completo():
    """Test de validación exitosa del request completo."""
    data = {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@universidad.edu",
            "dni": "12345678",
            "cuil": "20-12345678-9",
        },
        "universidad": {
            "nombre": "Universidad Nacional",
            "direccion": "Av. Principal 123",
            "codigo_postal": 5000,
        },
        "carrera": {
            "nombre": "Ingeniería en Sistemas",
            "codigo": "IS-2020",
        },
        "empresa": {
            "nombre": "TechCorp SA",
            "direccion": "Calle Tech 456",
            "codigo_postal": 5000,
        },
        "proyecto": {
            "nombre": "Desarrollo Web",
            "descripcion": "Plataforma de e-commerce",
            "numero": 1001,
        },
        "puesto": {
            "nombre": "Desarrollador Junior",
            "descripcion": "Desarrollo web",
        },
        "postulacion": {
            "numero": 5432,
            "fecha": "2026-01-05T10:30:00",
            "estado": "PENDIENTE",
        },
    }
    
    request = ComprobantePostulacionRequest(**data)
    
    assert request.estudiante.nombre == "Juan"
    assert request.universidad.nombre == "Universidad Nacional"
    assert request.postulacion.numero == 5432


def test_comprobante_postulacion_request_falta_estudiante():
    """Test que rechaza request sin datos de estudiante."""
    data = {
        "universidad": {
            "nombre": "Universidad Nacional",
            "direccion": "Av. Principal 123",
            "codigo_postal": 5000,
        },
        # Falta estudiante
    }
    
    with pytest.raises(ValidationError):
        ComprobantePostulacionRequest(**data)
