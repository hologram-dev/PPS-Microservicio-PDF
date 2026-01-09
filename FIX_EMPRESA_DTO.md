# ✅ Schema del Contrato Arreglado - Fixes HTTP 422

## 🔧 Cambios Realizados en `comprobante_contrato_schemas.py`

### 1. **UniversidadSchema.codigo_postal**
- **Antes**: `Optional[str]` (con min_length=1, max_length=10)
- **Ahora**: `Optional[int]` (con ge=1000, le=9999)

### 2. **EmpresaSchema.codigo_postal**  
- **Antes**: `Optional[str]` (con min_length=1, max_length=10)
- **Ahora**: `Optional[int]` (con ge=1000, le=9999)

### 3. **PuestoSchema.codigo**
- **Antes**: `Optional[str]`
- **Ahora**: `Optional[int]` (con ge=1)

### 4. **PuestoSchema.horas_dedicadas**
- **Antes**: `int` (ge=0)
- **Ahora**: `float` (ge=0)

---

## 📝 Payload Correcto (ahora validará ✅)

```json
{
  "estudiante": {
    "nombre": "María",
    "apellido": "González",
    "dni": "42856123",
    "email": "maria.gonzalez@gmail.com"
  },
  "universidad": {
    "nombre": "Universidad Nacional de Córdoba",
    "direccion": "Av. Haya de la Torre s/n, Ciudad Universitaria",
    "codigo_postal": 5000,
    "correo": "pasantias@unc.edu.ar",
    "telefono": "+543514334000"
  },
  "carrera": {
    "nombre": "Ingeniería en Sistemas de Información",
    "codigo": "ISI-2020",
    "plan_estudios": "Plan 2020"
  },
  "empresa": {
    "nombre": "TechnoSoft Argentina S.A.",
    "direccion": "Av. Colón 500, Piso 8",
    "codigo_postal": 5000,
    "telefono": "+543514238900",
    "codigo": 15847,
    "correo": "rrhh@technosoft.com.ar"
  },
  "proyecto": {
    "nombre": "Sistema de Gestión de Recursos Humanos",
    "fecha_inicio": "2026-02-01",
    "descripcion": "Desarrollo de un sistema integral",
    "numero": 2026001,
    "estado": "Activo",
    "fecha_fin": "2026-08-01"
  },
  "puesto": {
    "nombre": "Desarrollador Backend Junior",
    "descripcion": "Desarrollo de APIs REST con Python/FastAPI",
    "codigo": 1025,
    "horas_dedicadas": 30
  },
  "postulacion": {
    "numero": 450123,
    "fecha": "2025-12-15T10:30:00-03:00",
    "cantidad_materias_aprobadas": 28,
    "cantidad_materias_regulares": 3,
    "estado": "Aprobada"
  },
  "contrato": {
    "numero": 550234,
    "fecha_inicio": "2026-02-01",
    "fecha_fin": "2026-08-01",
    "fecha_emision": "2026-01-07",
    "estado": "Activo"
  }
}
```

---

## 🔄 IMPORTANTE: Rebuild Docker

FastAPI cachea la app en memoria, necesitas rebuild:

```bash
# Detener y reconstruir
docker compose down
docker compose up --build -d

# Verificar logs
docker compose logs pdf-service -f
```

---

## ✅ Verificar que Funciona

```bash
# Debe retornar HTTP 200 (no 422)
curl -X POST http://localhost:8001/api/v1/pdf/generate/comprobante_contrato \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante": {...},
    "universidad": {...},
    ...
  }' \
  --output contrato_test.pdf
```

Deberías ver un PDF generado exitosamente.
