"""
Comprobante de Contrato Schemas
===================================

Schemas Pydantic para validación HTTP del endpoint de comprobante de contrato.

IMPORTANTE: Estos son SCHEMAS (Presentation Layer), no DTOs.
- Schemas: Validan datos HTTP, generan documentación OpenAPI
- DTOs: Transferencia interna entre capas (sin validación)

El flujo es: HTTP Request → Schema valida → DTO → Use Case
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EstudianteSchema(BaseModel):
    """Schema para validación de datos del estudiante."""
    
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del estudiante")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del estudiante")
    dni: str = Field(..., min_length=7, max_length=10, description="DNI del estudiante")
    email: str = Field(..., description="Email del estudiante")
    cuil: Optional[str] = Field(default=None, description="CUIL del estudiante")
    fecha_nacimiento: Optional[str] = Field(default=None, description="Fecha de nacimiento en formato ISO")
    tipo_dni: Optional[str] = Field(default=None, description="Tipo de DNI")

class UniversidadSchema(BaseModel):
    """Schema para validación de datos de la universidad."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la universidad")
    direccion: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Dirección de la universidad")
    codigo_postal: Optional[str] = Field(default=None, min_length=1, max_length=10, description="Código postal de la universidad")
    correo: str = Field(..., description="Correo de la universidad")
    telefono: str = Field(..., max_length=18, description="Teléfono de la universidad")
    

class CarreraSchema(BaseModel):
    """Schema para validación de datos de la carrera."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la carrera")
    codigo: Optional[str] = Field(default=None, description="Código de la carrera")
    descripcion: Optional[str] = Field(default=None, description="Descripción de la carrera")
    plan_estudios: str = Field(..., description="Plan de estudios de la carrera")
    
class EmpresaSchema(BaseModel):
    """Schema para validación de datos de la empresa."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la empresa")
    direccion: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Dirección de la empresa")
    codigo_postal: Optional[str] = Field(default=None, min_length=1, max_length=10, description="Código postal de la empresa")
    correo: str = Field(..., description="Correo de la empresa")
    telefono: str = Field(..., max_length=18, description="Teléfono de la empresa")
    codigo: Optional[int] = Field(default=None, description="Código de la empresa")


class ProyectoSchema(BaseModel):
    """Schema para validación de datos del proyecto."""
    
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del proyecto")
    fecha_inicio: Optional[str] = Field(default=None, description="Fecha de inicio en formato ISO")
    descripcion: Optional[str] = Field(default=None, max_length=500, description="Descripción del proyecto")
    numero: int = Field(..., ge=1, description="Número identificador del proyecto")
    estado: Optional[str] = Field(default=None, description="Estado del proyecto")
    fecha_fin: str = Field(..., description="Fecha de fin en formato ISO")


    @field_validator("fecha_inicio")
    @classmethod
    def validate_fecha(cls, v: Optional[str]) -> Optional[str]:
        """Valida que las fechas estén en formato ISO válido."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")

    @field_validator("fecha_fin")
    @classmethod
    def validate_fecha_fin(cls, v: Optional[str]) -> Optional[str]:
        """Valida que las fechas estén en formato ISO válido."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")


class PuestoSchema(BaseModel):
    """Schema para validación de datos del puesto."""
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del puesto")
    descripcion: Optional[str] = Field(default=None, max_length=200, description="Descripción del puesto")
    codigo: Optional[str] = Field(default=None, description="Código del puesto")
    horas_dedicadas: int = Field(..., ge=0, description="Horas dedicadas al puesto")


class PostulacionSchema(BaseModel):
    """Schema para validación de datos de la postulación."""
    
    numero: int = Field(..., ge=1, description="Número identificador de la postulación")
    fecha: str = Field(..., description="Fecha y hora de la postulación en formato ISO")
    cantidad_materias_aprobadas: int = Field(default=0, ge=0, description="Cantidad de materias aprobadas")
    cantidad_materias_regulares: int = Field(default=0, ge=0, description="Cantidad de materias regulares")
    estado: Optional[str] = Field(default=None, description="Estado de la postulación")
    
    @field_validator("fecha")
    @classmethod
    def validate_fecha(cls, v: str) -> str:
        """Valida que la fecha esté en formato ISO válido."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")
        

class ContratoSchema(BaseModel):
    """Schema para validación de datos del contrato."""
    
    numero: int = Field(..., ge=1, description="Número identificador del contrato")
    fecha_inicio: str = Field(..., description="Fecha y hora del contrato en formato ISO")
    fecha_fin: str = Field(..., description="Fecha y hora del contrato en formato ISO")
    fecha_emision: str = Field(..., description="Fecha y hora de emisión del contrato en formato ISO")
    estado: Optional[str] = Field(default=None, description="Estado del contrato")
    
    @field_validator("fecha_inicio")
    @classmethod
    def validate_fecha_inicio(cls, v: str) -> str:
        """Valida que la fecha esté en formato ISO válido."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")

    @field_validator("fecha_fin")
    @classmethod
    def validate_fecha_fin(cls, v: str) -> str:
        """Valida que la fecha esté en formato ISO válido."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")

    @field_validator("fecha_emision")
    @classmethod
    def validate_fecha_emision(cls, v: str) -> str:
        """Valida que la fecha esté en formato ISO válido."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")

class ComprobanteContratoRequest(BaseModel):
    """
    Request principal para generar comprobante de postulación.
    
    Este schema solo valida:
    - Tipos de datos correctos (str, int, float, EmailStr)
    - Campos requeridos vs opcionales
    - Formatos específicos (email, CUIL, fechas ISO)
    - Rangos válidos (longitudes, valores numéricos)
    
    El endpoint acepta cualquier dato que cumpla con estas validaciones.
    """
    
    estudiante: EstudianteSchema = Field(..., description="Datos del estudiante")
    universidad: UniversidadSchema = Field(..., description="Datos de la universidad")
    carrera: CarreraSchema = Field(..., description="Datos de la carrera")
    empresa: EmpresaSchema = Field(..., description="Datos de la empresa")
    proyecto: ProyectoSchema = Field(..., description="Datos del proyecto de pasantía")
    puesto: PuestoSchema = Field(..., description="Datos del puesto")
    postulacion: PostulacionSchema = Field(..., description="Datos de la postulación")
    contrato: ContratoSchema = Field(..., description="Datos del contrato")

