"""
Comprobante de Postulación - Mocks
===================================

Datos de prueba (mocks) reutilizables para testing del
endpoint de comprobante de postulación.

Estos mocks se pueden usar en tests unitarios y de integración.
"""

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


def mock_estudiante_dto() -> EstudianteDTO:
    """Mock de datos de estudiante."""
    return EstudianteDTO(
        nombre="Juan",
        apellido="Pérez",
        email="juan.perez@universidad.edu",
        dni="12345678",
        cuil="20-12345678-9",
        fecha_nacimiento="1998-05-15",
        tipo_dni="DNI",
    )


def mock_universidad_dto() -> UniversidadDTO:
    """Mock de datos de universidad."""
    return UniversidadDTO(
        nombre="Universidad Nacional de Córdoba",
        direccion="Av. Haya de la Torre s/n, Ciudad Universitaria",
        codigo_postal=5000,
        correo="contacto@unc.edu.ar",
        telefono="+54 351 1234567",
    )


def mock_carrera_dto() -> CarreraDTO:
    """Mock de datos de carrera."""
    return CarreraDTO(
        nombre="Ingeniería en Sistemas de Información",
        codigo="IS-2020",
        descripcion="Ingeniería en Sistemas de Información",
        plan_estudios="Plan 2020",
    )


def mock_empresa_dto() -> EmpresaDTO:
    """Mock de datos de empresa."""
    return EmpresaDTO(
        nombre="TechCorp SA",
        direccion="Calle Tecnología 456, Córdoba",
        codigo_postal=5000,
        telefono="+54 351 9876543",
        codigo=1001,
    )


def mock_proyecto_dto() -> ProyectoDTO:
    """Mock de datos de proyecto."""
    return ProyectoDTO(
        nombre="Desarrollo Web E-commerce",
        descripcion="Desarrollo de plataforma de ventas online con React y Node.js",
        numero=1001,
        estado="ACTIVO",
        fecha_inicio="2026-02-01",
        fecha_fin="2026-08-01",
    )


def mock_puesto_dto() -> PuestoDTO:
    """Mock de datos de puesto."""
    return PuestoDTO(
        nombre="Desarrollador Junior",
        descripcion="Desarrollo de aplicaciones web con React y Node.js",
        codigo=501,
        horas_dedicadas=20.0,
    )


def mock_postulacion_dto() -> PostulacionDTO:
    """Mock de datos de postulación."""
    return PostulacionDTO(
        numero=5432,
        fecha="2026-01-05T10:30:00",
        estado="PENDIENTE",
        cantidad_materias_aprobadas=25,
        cantidad_materias_regulares=30,
    )


def mock_comprobante_postulacion_dto() -> ComprobantePostulacionDTO:
    """
    Mock completo de ComprobantePostulacionDTO.
    
    Retorna un DTO completo con todos los datos necesarios
    para generar un comprobante de postulación.
    """
    return ComprobantePostulacionDTO(
        estudiante=mock_estudiante_dto(),
        universidad=mock_universidad_dto(),
        carrera=mock_carrera_dto(),
        empresa=mock_empresa_dto(),
        proyecto=mock_proyecto_dto(),
        puesto=mock_puesto_dto(),
        postulacion=mock_postulacion_dto(),
    )


# Variaciones para testing de edge cases

def mock_estudiante_sin_fecha_nacimiento() -> EstudianteDTO:
    """Mock de estudiante sin fecha de nacimiento."""
    return EstudianteDTO(
        nombre="María",
        apellido="González",
        email="maria.gonzalez@universidad.edu",
        dni="87654321",
        cuil="27-87654321-3",
        fecha_nacimiento=None,
        tipo_dni="DNI",
    )


def mock_universidad_sin_contacto() -> UniversidadDTO:
    """Mock de universidad sin datos de contacto opcionales."""
    return UniversidadDTO(
        nombre="Universidad Tecnológica Nacional",
        direccion="Av. Vélez Sarsfield 1500",
        codigo_postal=5016,
        correo=None,
        telefono=None,
    )


def mock_proyecto_sin_fechas() -> ProyectoDTO:
    """Mock de proyecto sin fechas."""
    return ProyectoDTO(
        nombre="Sistema de Gestión Interna",
        descripcion="Sistema para gestión de recursos humanos",
        numero=2001,
        estado=None,
        fecha_inicio=None,
        fecha_fin=None,
    )


def mock_comprobante_minimo() -> ComprobantePostulacionDTO:
    """
    Mock con datos mínimos requeridos.
    
    Útil para testear validaciones de campos opcionales.
    """
    return ComprobantePostulacionDTO(
        estudiante=mock_estudiante_sin_fecha_nacimiento(),
        universidad=mock_universidad_sin_contacto(),
        carrera=CarreraDTO(
            nombre="Ingeniería Industrial",
            codigo="II-2019",
            descripcion=None,
            plan_estudios=None,
        ),
        empresa=EmpresaDTO(
            nombre="Industrias ACME",
            direccion="Zona Industrial Norte",
            codigo_postal=5000,
            telefono=None,
            codigo=None,
        ),
        proyecto=mock_proyecto_sin_fechas(),
        puesto=PuestoDTO(
            nombre="Analista de Procesos",
            descripcion="Análisis y mejora de procesos productivos",
            codigo=None,
            horas_dedicadas=15.0,
        ),
        postulacion=PostulacionDTO(
            numero=9999,
            fecha="2026-01-10T14:20:00",
            estado="APROBADA",
            cantidad_materias_aprobadas=0,
            cantidad_materias_regulares=0,
        ),
    )


# Para uso en JSON (request HTTP examples)

def comprobante_postulacion_dict() -> dict:
    """
    Retorna el mock como diccionario para ejemplos JSON.
    
    Útil para documentación de API y tests de integración.
    """
    return {
        "estudiante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan.perez@universidad.edu",
            "dni": "12345678",
            "cuil": "20-12345678-9",
            "fecha_nacimiento": "1998-05-15",
            "tipo_dni": "DNI",
        },
        "universidad": {
            "nombre": "Universidad Nacional de Córdoba",
            "direccion": "Av. Haya de la Torre s/n, Ciudad Universitaria",
            "codigo_postal": 5000,
            "correo": "contacto@unc.edu.ar",
            "telefono": "+54 351 1234567",
        },
        "carrera": {
            "nombre": "Ingeniería en Sistemas de Información",
            "codigo": "IS-2020",
            "descripcion": "Ingeniería en Sistemas de Información",
            "plan_estudios": "Plan 2020",
        },
        "empresa": {
            "nombre": "TechCorp SA",
            "direccion": "Calle Tecnología 456, Córdoba",
            "codigo_postal": 5000,
            "telefono": "+54 351 9876543",
            "codigo": 1001,
        },
        "proyecto": {
            "nombre": "Desarrollo Web E-commerce",
            "descripcion": "Desarrollo de plataforma de ventas online con React y Node.js",
            "numero": 1001,
            "estado": "ACTIVO",
            "fecha_inicio": "2026-02-01",
            "fecha_fin": "2026-08-01",
        },
        "puesto": {
            "nombre": "Desarrollador Junior",
            "descripcion": "Desarrollo de aplicaciones web con React y Node.js",
            "codigo": 501,
            "horas_dedicadas": 20.0,
        },
        "postulacion": {
            "numero": 5432,
            "fecha": "2026-01-05T10:30:00",
            "estado": "PENDIENTE",
            "cantidad_materias_aprobadas": 25,
            "cantidad_materias_regulares": 30,
        },
    }
