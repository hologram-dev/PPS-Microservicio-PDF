"""
Test de simplificación de DTOs con model_dump()
================================================

Verifica que el mapeo de Pydantic schemas a DTOs funciona correctamente.
"""
import pytest
from pydantic import ValidationError
from src.presentation.schemas.comprobante_postulacion_schemas import (
    ComprobantePostulacionRequest,
    EstudianteSchema,
    UniversidadSchema,
    CarreraSchema,
    EmpresaSchema,
    ProyectoSchema,
    PuestoSchema,
    PostulacionSchema,
)
from src.application.dto import (
    ComprobantePostulacionDTO,
    EstudianteDTO,
    UniversidadDTO,
    CarreraDTO,
    EmpresaDTO,
    ProyectoDTO,
    PuestoDTO,
    PostulacionDTO,
)


def test_estudiante_model_dump_mapping():
    """Verifica que model_dump() mapea correctamente EstudianteSchema → EstudianteDTO."""
    schema = EstudianteSchema(
        nombre="Juan",
        apellido="Pérez",
        dni="12345678",
        email="juan@example.com",
        cuil="20-12345678-9",
        fecha_nacimiento="1990-01-01",
        tipo_dni="DNI"
    )
    
    # Usar model_dump() para convertir
    dto = EstudianteDTO(**schema.model_dump())
    
    assert dto.nombre == "Juan"
    assert dto.apellido == "Pérez"
    assert dto.dni == "12345678"
    assert dto.email == "juan@example.com"


def test_universidad_model_dump_mapping():
    """Verifica mapeo de UniversidadSchema → UniversidadDTO."""
    schema = UniversidadSchema(
        nombre="UTN",
        direccion="Av. Universidad 123",
        codigo_postal="5000",
        correo="info@utn.edu.ar",
        telefono="123456789"
    )
    
    dto = UniversidadDTO(**schema.model_dump())
    
    assert dto.nombre == "UTN"
    assert dto.direccion == "Av. Universidad 123"


def test_full_comprobante_model_dump():
    """Verifica mapeo completo de ComprobantePostulacionRequest → ComprobantePostulacionDTO."""
    request_data = {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "dni": "12345678",
            "email": "juan@example.com",
            "cuil": "20-12345678-9",
            "fecha_nacimiento": "1990-01-01",
            "tipo_dni": "DNI"
        },
        "universidad": {
            "nombre": "UTN",
            "direccion": "Av. Universidad 123",
            "codigo_postal": "5000",
            "correo": "info@utn.edu.ar",
            "telefono": "123456789"
        },
        "carrera": {
            "nombre": "Ingeniería en Sistemas",
            "codigo": "K08",
            "descripcion": "Carrera de grado",
            "plan_estudios": "2008"
        },
        "empresa": {
            "nombre": "Tech Corp",
            "direccion": "Calle Empresa 456",
            "codigo_postal": "5001",
            "telefono": "987654321",
            "codigo": "EMP001"
        },
        "proyecto": {
            "nombre": "Proyecto Alpha",
            "fecha_inicio": "2024-01-01",
            "descripcion": "Desarrollo web",
            "numero": "PRY001",
            "estado": "activo",
            "fecha_fin": "2024-12-31"
        },
        "puesto": {
            "nombre": "Developer",
            "descripcion": "Full Stack Developer",
            "codigo": "DEV001",
            "horas_dedicadas": 40
        },
        "postulacion": {
            "numero": "POST001",
            "fecha": "2024-01-15",
            "cantidad_materias_aprobadas": 25,
            "cantidad_materias_regulares": 5,
            "estado": "aprobada"
        }
    }
    
    request = ComprobantePostulacionRequest(**request_data)
    
    # Mapear con model_dump() (simulando lo que hace el endpoint)
    comprobante_dto = ComprobantePostulacionDTO(
        estudiante=EstudianteDTO(**request.estudiante.model_dump()),
        universidad=UniversidadDTO(**request.universidad.model_dump()),
        carrera=CarreraDTO(**request.carrera.model_dump()),
        empresa=EmpresaDTO(**request.empresa.model_dump()),
        proyecto=ProyectoDTO(**request.proyecto.model_dump()),
        puesto=PuestoDTO(**request.puesto.model_dump()),
        postulacion=PostulacionDTO(**request.postulacion.model_dump()),
    )
    
    # Verificar que todos los datos se mapearon correctamente
    assert comprobante_dto.estudiante.nombre == "Juan"
    assert comprobante_dto.universidad.nombre == "UTN"
    assert comprobante_dto.carrera.nombre == "Ingeniería en Sistemas"
    assert comprobante_dto.empresa.nombre == "Tech Corp"
    assert comprobante_dto.proyecto.nombre == "Proyecto Alpha"
    assert comprobante_dto.puesto.nombre == "Developer"
    assert comprobante_dto.postulacion.numero == "POST001"


def test_model_dump_preserves_all_fields():
    """Verifica que model_dump() no pierde ningún campo."""
    schema = EstudianteSchema(
        nombre="Ana",
        apellido="García",
        dni="87654321",
        email="ana@example.com",
        cuil="27-87654321-4",
        fecha_nacimiento="1995-05-15",
        tipo_dni="DNI"
    )
    
    dumped = schema.model_dump()
    
    # Verificar que todos los campos estén presentes
    expected_fields = {"nombre", "apellido", "dni", "email", "cuil", "fecha_nacimiento", "tipo_dni"}
    assert set(dumped.keys()) == expected_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
