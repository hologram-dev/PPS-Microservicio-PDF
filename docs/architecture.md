# Clean Architecture - Documentación Técnica

## ¿Qué es Clean Architecture?

**Clean Architecture** es un patrón de diseño de software propuesto por Robert C. Martin (Uncle Bob) que organiza el código en capas concéntricas con una regla fundamental: **las dependencias solo pueden apuntar hacia adentro**.

### Principios Fundamentales

1. **Independencia de Frameworks**: El core de negocio no depende de bibliotecas externas
2. **Testabilidad**: Cada capa puede testearse de forma aislada
3. **Independencia de la UI**: Puedes cambiar de REST a GraphQL sin tocar el dominio
4. **Independencia de la BD**: El dominio no sabe cómo se persisten los datos
5. **Independencia de Agentes Externos**: Las reglas de negocio no conocen el mundo exterior

---

## Diagrama de Capas

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                     PRESENTATION LAYER                         │
│                  (FastAPI, Controllers)                        │
│                                                                │
│    ┌──────────────────────────────────────────────────────┐   │
│    │                                                      │   │
│    │                 APPLICATION LAYER                    │   │
│    │               (Use Cases, Services)                  │   │
│    │                                                      │   │
│    │    ┌────────────────────────────────────────────┐   │   │
│    │    │                                            │   │   │
│    │    │              DOMAIN LAYER                  │   │   │
│    │    │        (Entities, Value Objects)           │   │   │
│    │    │                                            │   │   │
│    │    │        ⭐ REGLAS DE NEGOCIO ⭐             │   │   │
│    │    │                                            │   │   │
│    │    └────────────────────────────────────────────┘   │   │
│    │                                                      │   │
│    └──────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                               ▲
                               │ Implementa interfaces
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                   INFRASTRUCTURE LAYER                         │
│            (ReportLab, Base de Datos, APIs)                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Capas en Este Proyecto

### 🔵 Domain Layer (`src/domain/`)

**Propósito**: El corazón de la aplicación. Contiene la lógica de negocio pura.

**Regla**: Esta capa NO importa NADA de las otras capas.

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **Entities** | `entities/` | Objetos con identidad única (PDFDocument) |
| **Value Objects** | `value_objects/` | Objetos inmutables (PDFStyle, ColorConfig) |
| **Exceptions** | `exceptions/` | Errores de reglas de negocio |
| **Interfaces** | `interfaces/` | Contratos (Ports) para inversión de dependencias |

```python
# Ejemplo: Entidad del dominio
@dataclass
class PDFDocument:
    id: UUID
    title: str
    sections: list[PDFSection]
    
    def add_section(self, section: PDFSection) -> None:
        # Regla de negocio
        if self._is_generated:
            raise ValueError("Cannot modify generated document")
        self.sections.append(section)
```

### 🟢 Application Layer (`src/application/`)

**Propósito**: Orquesta los casos de uso. Coordina entidades y servicios.

**Regla**: Solo depende del dominio. No sabe de FastAPI ni ReportLab.

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **Use Cases** | `use_cases/` | Acciones del sistema (GeneratePDF) - SON los servicios de aplicación |
| **DTOs** | `dto/` | Objetos de transferencia de datos |

```python
# Ejemplo: Caso de uso
class GeneratePDFUseCase:
    def __init__(self, pdf_generator: IPDFGenerator):
        self._generator = pdf_generator  # Interfaz, no implementación
    
    def execute(self, request: PDFRequestDTO) -> GeneratePDFResult:
        document = self._build_document(request)
        content = self._generator.generate(document)
        return GeneratePDFResult(content=content)
```

### 🟠 Infrastructure Layer (`src/infrastructure/`)

**Propósito**: Implementaciones concretas. Adapters que implementan los Ports.

**Regla**: Implementa las interfaces del dominio (inversión de dependencias).

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **PDF** | `pdf/` | Implementación con ReportLab |
| **Config** | `config/` | Configuración de la aplicación |
| **Persistence** | `persistence/` | Repositorios (futuro) |

```python
# Ejemplo: Implementación (Adapter)
class ReportLabGenerator(IPDFGenerator):  # Implementa la interfaz
    def generate(self, document: PDFDocument, style: PDFStyle) -> bytes:
        # Implementación específica con ReportLab
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        doc.build(elements)
        return buffer.read()
```

### 🟣 Presentation Layer (`src/presentation/`)

**Propósito**: Interfaz con el mundo exterior. Expone la API.

**Regla**: Traduce HTTP ↔ DTOs de aplicación.

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **API** | `api/` | Endpoints REST (FastAPI) |
| **Schemas** | `schemas/` | Validación con Pydantic |
| **Dependencies** | `dependencies/` | Inyección de dependencias |

```python
# Ejemplo: Endpoint
@router.post("/generate")
async def generate_pdf(
    request: PDFGenerateRequestSchema,  # Schema Pydantic
    use_case: GeneratePDFUseCase = Depends(get_generate_pdf_use_case)  # DI
):
    dto = convert_to_dto(request)  # Schema → DTO
    result = use_case.execute(dto)  # Llamada directa al caso de uso
    return PDFGenerateResponse(...)  # Result → Schema
```

---

## Flujo de una Request

```
1. HTTP Request
       │
       ▼
2. Presentation Layer (FastAPI)
   - Valida request con Pydantic Schema
   - Convierte a DTO
       │
       ▼
3. Application Layer (Use Case)
   - Orquesta la lógica
   - Crea/valida entidades del dominio
   - Llama a interfaces (no implementaciones)
       │
       ▼
4. Domain Layer (Entities)
   - Aplica reglas de negocio
   - Valida invariantes
       │
       ▼
5. Infrastructure Layer (ReportLab)
   - Implementa la generación real del PDF
       │
       ▼
6. Response
   - El resultado sube por las capas
   - Cada capa transforma al formato apropiado
```

---

## Beneficios de Esta Arquitectura

| Beneficio | Descripción |
|-----------|-------------|
| **Mantenibilidad** | Cambios en una capa no afectan otras |
| **Testabilidad** | Cada capa se testea independientemente |
| **Flexibilidad** | Fácil cambiar implementaciones (ej: de ReportLab a otro) |
| **Escalabilidad** | Estructura clara para crecer el proyecto |
| **Onboarding** | Nuevos desarrolladores entienden rápido |

---

## Comparación con Arquitectura Tradicional

| Aspecto | Tradicional | Clean Architecture |
|---------|-------------|-------------------|
| Dependencias | Aleatorias | Hacia el centro |
| Framework | Acoplado | Desacoplado |
| Testing | Difícil | Fácil |
| Cambiar BD | Retrabajo | Simple |
| Cambiar UI | Retrabajo | Simple |

---

## Referencias

- [Clean Architecture (libro)](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
- [The Clean Architecture (blog)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
