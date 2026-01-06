# Integración API Golang ↔ Microservicio PDF

## Descripción General

Este documento describe la arquitectura de integración entre la **API principal (Golang)** y el **Microservicio de PDF (Python)** para la generación de documentos PDF específicos del sistema de pasantías.

---

## Arquitectura de Integración

### Diagrama de Flujo

![Diagrama de arquitectura](C:/Users/AugustoPC/.gemini/antigravity/brain/8ae4864d-2292-47ce-8ffa-b8b880d01e82/uploaded_image_0_1767658873154.png)

### Flujo de una Petición

```
Frontend (Usuario)
        │
        │ 1. GET /v1/postulaciones/{id}/imprimir_recibo
        ▼
┌─────────────────────────────────────┐
│        API GOLANG (Backend)         │
│   (Modelado de datos de diseño)     │
│                                     │
│  • Consulta datos de la BD          │
│  • Arma el JSON con los DTOs        │
│  • Hace POST al microservicio       │
└─────────────────────────────────────┘
        │
        │ 2. POST /api/v1/receipt/generate
        │    Body: { estudianteDTO, proyectoDTO, postulacionDTO, ... }
        ▼
┌─────────────────────────────────────┐
│       MICROSERVICIO PDF (Python)    │
│                                     │
│  presentation/                      │
│    └── router.py (recibe POST)      │
│                                     │
│  application/dto/                   │
│    ├── business_dtos.py             │
│    │   (EstudianteDTO, EmpresaDTO,  │
│    │    ProyectoDTO, etc.)          │
│    ├── receipt_dto.py               │
│    │   (ComprobantePostulacionDTO)  │
│    └── agreement_dto.py             │
│        (ComprobanteContratoDTO)     │
│                                     │
│  application/use_cases/             │
│    ├── generate_receipt.py          │
│    └── generate_agreement.py        │
└─────────────────────────────────────┘
        │
        │ 3. Retorna PDF (bytes)
        ▼
    Frontend (descarga/visualiza)
```

---

## Modelo de Datos (Referencia)

![Modelo de datos completo](C:/Users/AugustoPC/.gemini/antigravity/brain/8ae4864d-2292-47ce-8ffa-b8b880d01e82/uploaded_image_1_1767658873154.jpg)

---

## DTOs Implementados

### Estructura de Archivos

```
src/application/dto/
├── __init__.py
├── pdf_request_dto.py      # DTOs genéricos del PDF
├── business_dtos.py        # DTOs de entidades de negocio
├── receipt_dto.py          # DTO para comprobante de postulación
└── agreement_dto.py        # DTO para contrato de pasantía
```

### DTOs de Entidades de Negocio (`business_dtos.py`)

| DTO | Campos | Descripción |
|-----|--------|-------------|
| `EstudianteDTO` | nombre, apellido, email, dni, cuil, fecha_nacimiento, tipo_dni | Datos del estudiante |
| `UniversidadDTO` | nombre, direccion, codigo_postal, correo, telefono | Institución educativa |
| `CarreraDTO` | nombre, codigo, descripcion, plan_estudios | Carrera del estudiante |
| `EmpresaDTO` | nombre, direccion, codigo_postal, telefono, codigo | Empresa oferente |
| `ProyectoDTO` | nombre, descripcion, numero, estado, fecha_inicio, fecha_fin | Proyecto de pasantía |
| `PuestoDTO` | nombre, descripcion, codigo, horas_dedicadas | Puesto al que postula |
| `PostulacionDTO` | numero, fecha, estado, cantidad_materias_aprobadas/regulares | Datos de postulación |
| `ContratoDTO` | numero, fecha_inicio, fecha_fin, fecha_emision, estado | Contrato de pasantía |

### DTOs Compuestos

#### `ComprobantePostulacionDTO` (receipt_dto.py)

Agrupa los DTOs necesarios para el **recibo de postulación**:

```python
@dataclass
class ComprobantePostulacionDTO:
    estudiante: EstudianteDTO
    universidad: UniversidadDTO
    carrera: CarreraDTO
    empresa: EmpresaDTO
    proyecto: ProyectoDTO
    puesto: PuestoDTO
    postulacion: PostulacionDTO
```

#### `ComprobanteContratoDTO` (agreement_dto.py)

Agrupa los DTOs necesarios para el **contrato de pasantía**:

```python
@dataclass
class ComprobanteContratoDTO:
    estudiante: EstudianteDTO
    universidad: UniversidadDTO
    carrera: CarreraDTO
    empresa: EmpresaDTO
    proyecto: ProyectoDTO
    puesto: PuestoDTO
    contrato: ContratoDTO
```

---

## Endpoints del Microservicio

### 1. Generar Comprobante de Postulación

```http
POST /api/v1/receipt/generate
Content-Type: application/json
```

**Request Body**:

```json
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
    "nombre": "Universidad Nacional",
    "direccion": "Av. Principal 123",
    "codigo_postal": 5000,
    "correo": "contacto@universidad.edu",
    "telefono": "+54 351 1234567"
  },
  "carrera": {
    "nombre": "Ingeniería en Sistemas",
    "codigo": "IS-2020",
    "descripcion": "Ingeniería en Sistemas de Información",
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
    "descripcion": "Desarrollo de aplicaciones web con React y Node.js",
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
```

**Response** (200 OK):

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="comprobante_postulacion_5432.pdf"

[PDF bytes]
```

---

### 2. Generar Contrato de Pasantía

```http
POST /api/v1/agreement/generate
Content-Type: application/json
```

**Request Body**:

```json
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
    "nombre": "Universidad Nacional",
    "direccion": "Av. Principal 123",
    "codigo_postal": 5000,
    "correo": "contacto@universidad.edu",
    "telefono": "+54 351 1234567"
  },
  "carrera": {
    "nombre": "Ingeniería en Sistemas",
    "codigo": "IS-2020",
    "descripcion": "Ingeniería en Sistemas de Información",
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
    "descripcion": "Desarrollo de aplicaciones web con React y Node.js",
    "codigo": 501,
    "horas_dedicadas": 20.0
  },
  "contrato": {
    "numero": 789,
    "fecha_inicio": "2026-02-01",
    "fecha_fin": "2026-08-01",
    "fecha_emision": "2026-01-15",
    "estado": "VIGENTE"
  }
}
```

**Response** (200 OK):

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="contrato_pasantia_789.pdf"

[PDF bytes]
```

---

## Mapeo Entidades Golang → Python DTOs

Basado en el diagrama de clases del modelo de datos:

| Entidad Golang | DTO Python | Campos Mapeados |
|----------------|------------|-----------------|
| **Estudiante** | `EstudianteDTO` | apellidoEstudiante→apellido, correoEstudiante→email, cuilEstudiante→cuil, dniEstudiante→dni, fechaNacimientoEstudiante→fecha_nacimiento, nombreEstudiante→nombre, tipoDNI→tipo_dni |
| **Universidad** | `UniversidadDTO` | codigoPostal→codigo_postal, correoUniversidad→correo, direccionUniversidad→direccion, nombreUniversidad→nombre, nroTelefono→telefono |
| **Carrera** | `CarreraDTO` | codCarrera→codigo, descripcionCarrera→descripcion, nombreCarrera→nombre |
| **Empresa** | `EmpresaDTO` | codEmpresa→codigo, codigoPostalEmpresa→codigo_postal, direccionEmpresa→direccion, nombreEmpresa→nombre, nroTelefonoEmpresa→telefono |
| **Proyecto** | `ProyectoDTO` | descripcionProyecto→descripcion, nombreProyecto→nombre, numeroProyecto→numero, fechaFinProyecto→fecha_fin, fechaInicioActivacion→fecha_inicio |
| **Puesto** | `PuestoDTO` | codPuesto→codigo, descripcionPuesto→descripcion, nombrePuesto→nombre, horasDedicadas→horas_dedicadas |
| **Postulacion** | `PostulacionDTO` | cantMateriasAprobadas→cantidad_materias_aprobadas, cantMateriasRegulares→cantidad_materias_regulares, fechaHoraPostulacion→fecha, numeroPostulacion→numero |
| **Contrato** | `ContratoDTO` | fechaEmisionContrato→fecha_emision, fechaFinContrato→fecha_fin, fechaInicioContrato→fecha_inicio, numeroContrato→numero |
| **EstadoPostulacion** | (en PostulacionDTO) | nombreEstadoPostulacion→estado |
| **EstadoContrato** | (en ContratoDTO) | nombreEstadoContrato→estado |

---

## Cómo Funciona el Flujo

### 1. La API Golang construye el JSON

```go
// En el handler de Golang
func HandleImprimirRecibo(w http.ResponseWriter, r *http.Request) {
    // Consultar datos de la BD
    estudiante := db.GetEstudiante(id)
    postulacion := db.GetPostulacion(postulacionId)
    // ... más consultas
    
    // Construir el JSON
    body := map[string]interface{}{
        "estudiante": map[string]interface{}{
            "nombre": estudiante.Nombre,
            "apellido": estudiante.Apellido,
            // ...
        },
        "postulacion": map[string]interface{}{
            "numero": postulacion.Numero,
            // ...
        },
        // ... más DTOs
    }
    
    // POST al microservicio
    resp, _ := http.Post("http://pdf-service/api/v1/receipt/generate", 
                         "application/json", 
                         json.Marshal(body))
    
    // Retornar el PDF
    io.Copy(w, resp.Body)
}
```

### 2. El Microservicio recibe y procesa

```python
# router.py (pseudo-código)
@router.post("/receipt/generate")
async def generate_receipt(request: ComprobantePostulacionRequest):
    # Pydantic valida y convierte a DTO
    dto = ComprobantePostulacionDTO(
        estudiante=EstudianteDTO(**request.estudiante),
        postulacion=PostulacionDTO(**request.postulacion),
        # ...
    )
    
    # UseCase traduce a PDFDocument y genera
    result = receipt_use_case.execute(dto)
    
    return StreamingResponse(result, media_type="application/pdf")
```

---

## Próximos Pasos

- [ ] Crear schemas Pydantic para validación en `presentation/schemas/`
- [ ] Implementar UseCases: `GenerateReceiptUseCase`, `GenerateAgreementUseCase`
- [ ] Agregar endpoints en `router.py`
- [ ] Documentar con Swagger/OpenAPI
- [ ] Coordinar estructura JSON final con equipo Golang
