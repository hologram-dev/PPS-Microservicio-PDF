"""
Comprobante de Postulación Schemas
===================================

Schemas Pydantic para validación HTTP del endpoint de comprobante de postulación.

IMPORTANTE: Estos son SCHEMAS (Presentation Layer), no DTOs.
- Schemas: Validan datos HTTP, generan documentación OpenAPI
- DTOs: Transferencia interna entre capas (sin validación)

El flujo es: HTTP Request → Schema valida → DTO → Use Case
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, EmailStr


class EstudianteSchema(BaseModel):
    """Schema para validación de datos del estudiante.
    
    Campos requeridos: nombre, apellido, dni
    Campos opcionales: email, cuil, fecha_nacimiento, tipo_dni
    """
    
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del estudiante")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del estudiante")
    dni: str = Field(..., min_length=7, max_length=10, description="DNI del estudiante")
    email: Optional[EmailStr] = Field(default=None, description="Email del estudiante")
    cuil: Optional[str] = Field(default=None, pattern=r"^\d{2}-\d{7,8}-\d{1}$", description="CUIL en formato XX-XXXXXXXX-X")
    fecha_nacimiento: Optional[str] = Field(default=None, description="Fecha de nacimiento en formato ISO (YYYY-MM-DD)")
    tipo_dni: str = Field(default="DNI", max_length=20, description="Tipo de documento")
    
    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_fecha_nacimiento(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la fecha de nacimiento sea válida y en el pasado."""
        if v is None:
            return v
        try:
            fecha = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if fecha > datetime.now():
                raise ValueError("La fecha de nacimiento no puede estar en el futuro")
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")


class UniversidadSchema(BaseModel):
    """Schema para validación de datos de la universidad.
    
    Campos requeridos: nombre, direccion
    Campos opcionales: codigo_postal, correo, telefono
    """
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la universidad")
    direccion: str = Field(..., min_length=1, max_length=300, description="Dirección de la universidad")
    codigo_postal: Optional[int] = Field(default=None, ge=1000, le=9999, description="Código postal")
    correo: Optional[str] = Field(default=None, description="Email de contacto de la universidad")
    telefono: Optional[str] = Field(default=None, max_length=14, description="Teléfono de contacto")
    
    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: Optional[str]) -> Optional[str]:
        """Valida el formato del email si está presente."""
        if v is None:
            return v
        if "@" not in v or "." not in v:
            raise ValueError("Formato de email inválido")
        return v


class CarreraSchema(BaseModel):
    """Schema para validación de datos de la carrera.
    
    Campos requeridos: nombre
    Campos opcionales: codigo, descripcion, plan_estudios
    """
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la carrera")
    codigo: Optional[str] = Field(default=None, min_length=1, max_length=50, description="Código de la carrera")
    descripcion: Optional[str] = Field(default=None, max_length=100, description="Descripción de la carrera")
    plan_estudios: Optional[str] = Field(default=None, max_length=100, description="Plan de estudios")


class EmpresaSchema(BaseModel):
    """Schema para validación de datos de la empresa.
    
    Campos requeridos: nombre
    Campos opcionales: direccion, codigo_postal, telefono, codigo
    """
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la empresa")
    direccion: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Dirección de la empresa")
    codigo_postal: Optional[int] = Field(default=None, ge=1000, le=9999, description="Código postal")
    telefono: Optional[str] = Field(default=None, max_length=50, description="Teléfono de contacto")
    codigo: Optional[int] = Field(default=None, ge=1, description="Código identificador de la empresa")


class ProyectoSchema(BaseModel):
    """Schema para validación de datos del proyecto.
    
    Campos requeridos: nombre, fecha_inicio
    Campos opcionales: descripcion, numero, estado, fecha_fin
    """
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del proyecto")
    fecha_inicio: Optional[str] = Field(default=None, description="Fecha de inicio en formato ISO")
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=1000, description="Descripción del proyecto")
    numero: Optional[int] = Field(default=None, ge=1, description="Número identificador del proyecto")
    estado: Optional[str] = Field(default=None, max_length=50, description="Estado del proyecto")
    fecha_fin: Optional[str] = Field(default=None, description="Fecha de fin en formato ISO")
    
    @field_validator("fecha_inicio", "fecha_fin")
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


class PuestoSchema(BaseModel):
    """Schema para validación de datos del puesto.
    
    Campos requeridos: nombre
    Campos opcionales: descripcion, codigo, horas_dedicadas
    """
    
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del puesto")
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=1000, description="Descripción del puesto")
    codigo: Optional[int] = Field(default=None, ge=1, description="Código identificador del puesto")
    horas_dedicadas: float = Field(default=0.0, ge=0.0, le=168.0, description="Horas semanales dedicadas")


class PostulacionSchema(BaseModel):
    """Schema para validación de datos de la postulación.
    
    Campos requeridos: numero, fecha, cantidad_materias_aprobadas, cantidad_materias_regulares
    Campos opcionales: estado
    """
    
    numero: int = Field(..., ge=1, description="Número identificador de la postulación")
    fecha: str = Field(..., description="Fecha y hora de la postulación en formato ISO")
    cantidad_materias_aprobadas: int = Field(..., ge=0, description="Cantidad de materias aprobadas")
    cantidad_materias_regulares: int = Field(..., ge=0, description="Cantidad de materias regulares")
    estado: str = Field(default="Pendiente", min_length=1, max_length=50, description="Estado de la postulación")
    
    @field_validator("fecha")
    @classmethod
    def validate_fecha(cls, v: str) -> str:
        """Valida que la fecha esté en formato ISO válido."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {str(e)}")


class ComprobantePostulacionRequest(BaseModel):
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

