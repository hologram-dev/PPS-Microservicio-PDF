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
    """Schema para validación de datos del estudiante."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del estudiante",
        examples=["Juan"],
    )
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Apellido del estudiante",
        examples=["Pérez"],
    )
    email: EmailStr = Field(
        ...,
        description="Email del estudiante",
        examples=["juan.perez@universidad.edu"],
    )
    dni: str = Field(
        ...,
        min_length=7,
        max_length=10,
        description="DNI del estudiante",
        examples=["12345678"],
    )
    cuil: str = Field(
        ...,
        pattern=r"^\d{2}-\d{7,8}-\d{1}$",
        description="CUIL en formato XX-XXXXXXXX-X",
        examples=["20-12345678-9"],
    )
    fecha_nacimiento: Optional[str] = Field(
        default=None,
        description="Fecha de nacimiento en formato ISO (YYYY-MM-DD)",
        examples=["1998-05-15"],
    )
    tipo_dni: str = Field(
        default="DNI",
        max_length=20,
        description="Tipo de documento",
        examples=["DNI", "LC", "LE"],
    )
    
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
    """Schema para validación de datos de la universidad."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre de la universidad",
        examples=["Universidad Nacional de Córdoba"],
    )
    direccion: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Dirección de la universidad",
        examples=["Av. Haya de la Torre s/n, Ciudad Universitaria"],
    )
    codigo_postal: int = Field(
        ...,
        ge=1000,
        le=9999,
        description="Código postal",
        examples=[5000],
    )
    correo: Optional[str] = Field(
        default=None,
        description="Email de contacto de la universidad",
        examples=["contacto@universidad.edu"],
    )
    telefono: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Teléfono de contacto",
        examples=["+54 351 1234567"],
    )
    
    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: Optional[str]) -> Optional[str]:
        """Valida el formato del email si está presente."""
        if v is None:
            return v
        # Validación básica de email
        if "@" not in v or "." not in v:
            raise ValueError("Formato de email inválido")
        return v


class CarreraSchema(BaseModel):
    """Schema para validación de datos de la carrera."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre de la carrera",
        examples=["Ingeniería en Sistemas de Información"],
    )
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código de la carrera",
        examples=["IS-2020"],
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción de la carrera",
    )
    plan_estudios: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Plan de estudios",
        examples=["Plan 2020"],
    )


class EmpresaSchema(BaseModel):
    """Schema para validación de datos de la empresa."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre de la empresa",
        examples=["TechCorp SA"],
    )
    direccion: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Dirección de la empresa",
        examples=["Calle Tecnología 456"],
    )
    codigo_postal: int = Field(
        ...,
        ge=1000,
        le=9999,
        description="Código postal",
        examples=[5000],
    )
    telefono: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Teléfono de contacto",
        examples=["+54 351 9876543"],
    )
    codigo: Optional[int] = Field(
        default=None,
        ge=1,
        description="Código identificador de la empresa",
        examples=[1001],
    )


class ProyectoSchema(BaseModel):
    """Schema para validación de datos del proyecto."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del proyecto",
        examples=["Desarrollo Web E-commerce"],
    )
    descripcion: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Descripción del proyecto",
        examples=["Desarrollo de plataforma de ventas online"],
    )
    numero: int = Field(
        ...,
        ge=1,
        description="Número identificador del proyecto",
        examples=[1001],
    )
    estado: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Estado del proyecto",
        examples=["ACTIVO", "FINALIZADO", "EN_ESPERA"],
    )
    fecha_inicio: Optional[str] = Field(
        default=None,
        description="Fecha de inicio en formato ISO",
        examples=["2026-02-01"],
    )
    fecha_fin: Optional[str] = Field(
        default=None,
        description="Fecha de fin en formato ISO",
        examples=["2026-08-01"],
    )
    
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
    """Schema para validación de datos del puesto."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del puesto",
        examples=["Desarrollador Junior"],
    )
    descripcion: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Descripción del puesto",
        examples=["Desarrollo de aplicaciones web con React y Node.js"],
    )
    codigo: Optional[int] = Field(
        default=None,
        ge=1,
        description="Código identificador del puesto",
        examples=[501],
    )
    horas_dedicadas: float = Field(
        default=0.0,
        ge=0.0,
        le=168.0,  # Máximo horas en una semana
        description="Horas semanales dedicadas",
        examples=[20.0],
    )


class PostulacionSchema(BaseModel):
    """Schema para validación de datos de la postulación."""
    
    numero: int = Field(
        ...,
        ge=1,
        description="Número identificador de la postulación",
        examples=[5432],
    )
    fecha: str = Field(
        ...,
        description="Fecha y hora de la postulación en formato ISO",
        examples=["2026-01-05T10:30:00"],
    )
    estado: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Estado de la postulación",
        examples=["PENDIENTE", "APROBADA", "RECHAZADA"],
    )
    cantidad_materias_aprobadas: int = Field(
        default=0,
        ge=0,
        description="Cantidad de materias aprobadas",
        examples=[25],
    )
    cantidad_materias_regulares: int = Field(
        default=0,
        ge=0,
        description="Cantidad de materias regulares",
        examples=[30],
    )
    
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
    
    Este schema agrupa todos los datos necesarios para generar
    el comprobante. FastAPI lo usará para validar el request HTTP
    y generar la documentación OpenAPI.
    """
    
    estudiante: EstudianteSchema = Field(
        ...,
        description="Datos del estudiante",
    )
    universidad: UniversidadSchema = Field(
        ...,
        description="Datos de la universidad",
    )
    carrera: CarreraSchema = Field(
        ...,
        description="Datos de la carrera",
    )
    empresa: EmpresaSchema = Field(
        ...,
        description="Datos de la empresa",
    )
    proyecto: ProyectoSchema = Field(
        ...,
        description="Datos del proyecto de pasantía",
    )
    puesto: PuestoSchema = Field(
        ...,
        description="Datos del puesto",
    )
    postulacion: PostulacionSchema = Field(
        ...,
        description="Datos de la postulación",
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "estudiante": {
                        "nombre": "Juan",
                        "apellido": "Pérez",
                        "email": "juan.perez@universidad.edu",
                        "dni": "12345678",
                        "cuil": "20-12345678-9",
                        "fecha_nacimiento": "1998-05-15",
                        "tipo_dni": "DNI"
                    },
                    "universidad": {
                        "nombre": "Universidad Nacional de Córdoba",
                        "direccion": "Av. Haya de la Torre s/n",
                        "codigo_postal": 5000,
                        "correo": "contacto@universidad.edu",
                        "telefono": "+54 351 1234567"
                    },
                    "carrera": {
                        "nombre": "Ingeniería en Sistemas de Información",
                        "codigo": "IS-2020",
                        "descripcion": "Ingeniería en Sistemas",
                        "plan_estudios": "Plan 2020"
                    },
                    "empresa": {
                        "nombre": "TechCorp SA",
                        "direccion": "Calle Tecnología 456",
                        "codigo_postal": 5000,
                        "telefono": "+54 351 9876543",
                        "codigo": 1001
                    },
                    "proyecto": {
                        "nombre": "Desarrollo Web E-commerce",
                        "descripcion": "Desarrollo de plataforma de ventas online",
                        "numero": 1001,
                        "estado": "ACTIVO",
                        "fecha_inicio": "2026-02-01",
                        "fecha_fin": "2026-08-01"
                    },
                    "puesto": {
                        "nombre": "Desarrollador Junior",
                        "descripcion": "Desarrollo de aplicaciones web",
                        "codigo": 501,
                        "horas_dedicadas": 20.0
                    },
                    "postulacion": {
                        "numero": 5432,
                        "fecha": "2026-01-05T10:30:00",
                        "estado": "PENDIENTE",
                        "cantidad_materias_aprobadas": 25,
                        "cantidad_materias_regulares": 30
                    }
                }
            ]
        }
    }
