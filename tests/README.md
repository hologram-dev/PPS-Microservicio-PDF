# Guía de Testing - PDF Microservice
## Optimizaciones Implementadas

Esta guía explica cómo ejecutar los tests unitarios y de stress para verificar las optimizaciones implementadas.

---

## 📋 Instalación de Dependencias

```bash
# Instalar dependencias de testing
pip install -r requirements-test.txt
```

---

## ✅ Tests Unitarios

### 1. Test de Caché de Estilos PDF

Verifica que los estilos de ReportLab se cachean correctamente con `@lru_cache(maxsize=16)`.

```bash
pytest tests/unit/test_style_cache.py -v
```

**Qué verifica**:
- Cache hit/miss funciona correctamente
- Diferentes estilos se cachean por separado
- Estadísticas de cache (`cache_info()`)
- Respeta el `maxsize=16`

---

### 2. Test de Caché de Fechas

Verifica que el parsing de fechas se cachea con `@lru_cache(maxsize=128)`.

```bash
pytest tests/unit/test_date_cache.py -v
```

**Qué verifica**:
- Fechas parseadas se cachean
- Diferentes fechas se cachean por separado
- Manejo de `None`
- Diferentes formatos (datetime con hora, solo fecha)

---

### 3. Test de Mapeo de DTOs

Verifica que `model_dump()` funciona correctamente para simplificar el mapeo.

```bash
pytest tests/unit/test_dto_mapping.py -v
```

**Qué verifica**:
- `model_dump()` mapea todos los campos
- No se pierden datos en la conversión
- Funciona para todos los schemas (Estudiante, Universidad, etc.)

---

### 4. Test de Rate Limiting

Verifica que SlowAPI bloquea requests que exceden el límite.

```bash
pytest tests/integration/test_rate_limiting.py -v
```

**Qué verifica**:
- Límite de 200/min en `/health`
- Request 201 retorna HTTP 429
- Formato de respuesta de error
- Límites independientes por endpoint

---

### Ejecutar Todos los Tests Unitarios

```bash
# Con coverage
pytest tests/unit tests/integration -v --cov=src --cov-report=html

# Sin coverage
pytest tests/unit tests/integration -v
```

---

## ⚡ Tests de Stress (Load Testing)

### Opción 1: Locust (Recomendado)

**Interfaz Web** (recomendado para exploración):

```bash
locust -f tests/load/locustfile.py --host http://localhost:8001
```

Abrir http://localhost:8089 y configurar:
- **Number of users**: 50 (usuarios simultáneos)
- **Spawn rate**: 5 (usuarios/segundo)

**Modo Headless** (para CI/CD):

```bash
# Test de 5 minutos con 50 usuarios
locust -f tests/load/locustfile.py --host http://localhost:8001 \
       -u 50 -r 5 --run-time 5m --headless

# Test rápido (1 minuto, 20 usuarios)
locust -f tests/load/locustfile.py --host http://localhost:8001 \
       -u 20 -r 10 --run-time 1m --headless
```

**Qué mide**:
- Throughput (req/s)
- Response times (P50, P95, P99)
- Error rate
- Requests totales

**Escenarios incluidos**:
- `PDFUser`: Usuario normal (espera 1-3s entre requests)
- `HeavyLoadUser`: Carga pesada (espera 0.1-0.5s)

---

### Opción 2: Benchmark Script

Script Python async para benchmarks rápidos y comparaciones.

```bash
python tests/benchmark/benchmark.py
```

**Qué mide**:
- Requests secuenciales
- Requests concurrentes (10 concurrencia)
- Requests concurrentes (20 concurrencia)
- Comparación de P50, P95, P99
- Throughput

**Ventajas**:
- Más rápido que Locust
- Útil para comparaciones antes/después
- Salida en consola clara

---

## 📊 Métricas Objetivo

Después de las optimizaciones, se esperan estos resultados:

| Métrica | Objetivo Mínimo | Objetivo Ideal |
|---------|-----------------|----------------|
| **Throughput** | 50 req/s | 200+ req/s |
| **P50 Latency** | < 500ms | < 200ms |
| **P95 Latency** | < 2s | < 1s |
| **P99 Latency** | < 5s | < 2s |
| **Error Rate** | < 1% | < 0.1% |

---

## 🔍 Verificación Manual de Workers

Verificar que Gunicorn inició 5 workers:

```bash
# Iniciar servicio
sudo docker compose up pdf-service --build

# En otra terminal
sudo docker compose logs pdf-service | grep "Booting worker"
```

**Resultado esperado**:
```
[INFO] Booting worker with pid: 12
[INFO] Booting worker with pid: 13
[INFO] Booting worker with pid: 14
[INFO] Booting worker with pid: 15
[INFO] Booting worker with pid: 16
```

---

## 🐛 Troubleshooting

### Error: "No module named 'locust'"
```bash
pip install -r requirements-test.txt
```

### Error: "Connection refused"
Verificar que el servicio está corriendo:
```bash
curl http://localhost:8001/api/v1/pdf/health
```

### Tests de caché fallan
Limpiar cache antes de ejecutar:
```python
# En el test
parse_iso_to_spanish_argentina.cache_clear()
generator._create_styles.cache_clear()
```

---

## 📝 Comandos Rápidos

```bash
# Tests unitarios rápidos
pytest tests/unit -v -x

# Load test rápido (1 min)
locust -f tests/load/locustfile.py --host http://localhost:8001 -u 20 -r 10 --run-time 1m --headless

# Benchmark
python tests/benchmark/benchmark.py

# Coverage completo
pytest tests/ -v --cov=src --cov-report=term-missing
```
