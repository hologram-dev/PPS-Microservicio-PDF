"""
Business DTOs
=============

DTOs que representan las entidades de negocio que llegan
desde la API de Golang.

Estos DTOs reflejan la estructura del JSON que viene en el
request body de los POST desde el backend principal.

Estructura del JSON:
{
    "estudiante": { ... },
    "empresa": { ... },
    "proyecto": { ... },
    "postulacion": { ... },
    "puesto": { ... },
    "carrera": { ... },
    "universidad": { ... },
    "contrato": { ... }
}
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EstudianteDTO:
    """
    DTO con los datos del estudiante.
    
    Campos requeridos: nombre, apellido, dni
    Campos opcionales: email, cuil, fecha_nacimiento, tipo_dni
    """
    nombre: str
    apellido: str
    dni: str
    email: Optional[str] = None
    cuil: Optional[str] = None
    fecha_nacimiento: Optional[str] = None  # ISO format
    tipo_dni: str = "DNI"


@dataclass
class UniversidadDTO:
    """
    DTO con los datos de la universidad.
    
    Campos requeridos: nombre, direccion
    Campos opcionales: codigo_postal, correo, telefono
    """
    nombre: str
    direccion: str
    codigo_postal: Optional[int] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None


@dataclass
class CarreraDTO:
    """
    DTO con los datos de la carrera.
    
    Campos requeridos: nombre
    Campos opcionales: codigo, descripcion, plan_estudios
    """
    nombre: str
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    plan_estudios: Optional[str] = None


@dataclass
class EmpresaDTO:
    """
    DTO con los datos de la empresa.
    
    Campos requeridos: nombre
    Campos opcionales: direccion, codigo_postal, telefono, codigo
    """
    nombre: str
    direccion: Optional[str] = None
    codigo_postal: Optional[int] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[int] = None


@dataclass
class ProyectoDTO:
    """
    DTO con los datos del proyecto de pasantía.
    
    Campos requeridos: nombre, fecha_inicio
    Campos opcionales: descripcion, numero, estado, fecha_fin
    """
    nombre: str
    fecha_inicio: Optional[str] = None  # ISO format
    descripcion: Optional[str] = None
    numero: Optional[int] = None
    estado: Optional[str] = None
    fecha_fin: Optional[str] = None  # ISO format


@dataclass
class PuestoDTO:
    """
    DTO con los datos del puesto.
    
    Campos requeridos: nombre
    Campos opcionales: descripcion, codigo, horas_dedicadas
    """
    nombre: str
    descripcion: Optional[str] = None
    codigo: Optional[int] = None
    horas_dedicadas: float = 0.0


@dataclass
class PostulacionDTO:
    """
    DTO con los datos de la postulación.
    
    Campos requeridos: numero, fecha, cantidad_materias_aprobadas, cantidad_materias_regulares
    Campos opcionales: estado
    """
    numero: int
    fecha: str  # ISO format datetime
    cantidad_materias_aprobadas: int
    cantidad_materias_regulares: int
    estado: str = "Pendiente"


@dataclass
class ContratoDTO:
    """
    DTO con los datos del contrato de pasantía.
    
    Mapea desde la entidad Contrato de Golang.
    """
    numero: int
    fecha_inicio: str  # ISO format date
    fecha_fin: str  # ISO format date
    fecha_emision: str  # ISO format date
    estado: str
