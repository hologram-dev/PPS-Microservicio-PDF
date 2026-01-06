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
    
    Mapea desde la entidad Estudiante de Golang.
    """
    nombre: str
    apellido: str
    email: str
    dni: str
    cuil: str
    fecha_nacimiento: Optional[str] = None  # ISO format
    tipo_dni: str = "DNI"


@dataclass
class UniversidadDTO:
    """
    DTO con los datos de la universidad.
    
    Mapea desde la entidad Universidad de Golang.
    """
    nombre: str
    direccion: str
    codigo_postal: int
    correo: Optional[str] = None
    telefono: Optional[str] = None


@dataclass
class CarreraDTO:
    """
    DTO con los datos de la carrera.
    
    Mapea desde la entidad Carrera de Golang.
    """
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    plan_estudios: Optional[str] = None


@dataclass
class EmpresaDTO:
    """
    DTO con los datos de la empresa.
    
    Mapea desde la entidad Empresa de Golang.
    """
    nombre: str
    direccion: str
    codigo_postal: int
    telefono: Optional[str] = None
    codigo: Optional[int] = None


@dataclass
class ProyectoDTO:
    """
    DTO con los datos del proyecto de pasantía.
    
    Mapea desde la entidad Proyecto de Golang.
    """
    nombre: str
    descripcion: str
    numero: int
    estado: Optional[str] = None
    fecha_inicio: Optional[str] = None  # ISO format
    fecha_fin: Optional[str] = None  # ISO format


@dataclass
class PuestoDTO:
    """
    DTO con los datos del puesto.
    
    Mapea desde la entidad Puesto de Golang.
    """
    nombre: str
    descripcion: str
    codigo: Optional[int] = None
    horas_dedicadas: float = 0.0


@dataclass
class PostulacionDTO:
    """
    DTO con los datos de la postulación.
    
    Mapea desde la entidad Postulacion de Golang.
    """
    numero: int
    fecha: str  # ISO format datetime
    estado: str
    cantidad_materias_aprobadas: int = 0
    cantidad_materias_regulares: int = 0


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
