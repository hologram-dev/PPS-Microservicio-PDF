"""
Benchmark Script - Comparación Antes/Después
=============================================

Script para medir y comparar performance antes y después de optimizaciones.

Uso:
    python tests/benchmark/benchmark.py
"""
import asyncio
import time
import statistics
from typing import List
import httpx


BASE_URL = "http://localhost:8001"

PAYLOAD = {
    "estudiante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@example.com",
        "cuil": "20-12345678-9",
        "fecha_nacimiento": "1990-01-01",
        "tipo_dni": "DNI"
    },
    "universidad": {
        "nombre": "UTN",
        "direccion": "Av. Universidad 123",
        "codigo_postal": "5000",
        "correo": "info@utn.edu.ar",
        "telefono": "123456789"
    },
    "carrera": {
        "nombre": "Ingeniería en Sistemas",
        "codigo": "K08",
        "descripcion": "Carrera de grado",
        "plan_estudios": "2008"
    },
    "empresa": {
        "nombre": "Tech Corp",
        "direccion": "Calle Empresa 456",
        "codigo_postal": "5001",
        "telefono": "987654321",
        "codigo": "EMP001"
    },
    "proyecto": {
        "nombre": "Proyecto Alpha",
        "fecha_inicio": "2024-01-01",
        "descripcion": "Desarrollo web",
        "numero": "PRY001",
        "estado": "activo",
        "fecha_fin": "2024-12-31"
    },
    "puesto": {
        "nombre": "Developer",
        "descripcion": "Full Stack Developer",
        "codigo": "DEV001",
        "horas_dedicadas": 40
    },
    "postulacion": {
        "numero": "POST001",
        "fecha": "2024-01-15",
        "cantidad_materias_aprobadas": 25,
        "cantidad_materias_regulares": 5,
        "estado": "aprobada"
    }
}


async def single_request(client: httpx.AsyncClient) -> float:
    """Hace un request y retorna el tiempo de respuesta en ms."""
    start = time.perf_counter()
    response = await client.post(
        f"{BASE_URL}/api/v1/pdf/generate/comprobante_postulacion",
        json=PAYLOAD,
        timeout=30.0
    )
    end = time.perf_counter()
    
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")
    
    return (end - start) * 1000  # Convertir a ms


async def sequential_benchmark(num_requests: int = 100) -> List[float]:
    """Ejecuta requests secuenciales y retorna tiempos."""
    print(f"\n🔄 Ejecutando {num_requests} requests SECUENCIALES...")
    times = []
    
    async with httpx.AsyncClient() as client:
        for i in range(num_requests):
            try:
                response_time = await single_request(client)
                times.append(response_time)
                if (i + 1) % 10 == 0:
                    print(f"  ✓ Completados {i + 1}/{num_requests}")
            except Exception as e:
                print(f"  ✗ Error en request {i + 1}: {e}")
    
    return times


async def concurrent_benchmark(num_requests: int = 100, concurrency: int = 10) -> List[float]:
    """Ejecuta requests concurrentes y retorna tiempos."""
    print(f"\n⚡ Ejecutando {num_requests} requests CONCURRENTES (concurrency={concurrency})...")
    times = []
    
    async with httpx.AsyncClient() as client:
        for batch in range(0, num_requests, concurrency):
            batch_size = min(concurrency, num_requests - batch)
            tasks = [single_request(client) for _ in range(batch_size)]
            
            try:
                batch_times = await asyncio.gather(*tasks)
                times.extend(batch_times)
                print(f"  ✓ Completados {batch + batch_size}/{num_requests}")
            except Exception as e:
                print(f"  ✗ Error en batch: {e}")
    
    return times


def print_stats(times: List[float], label: str):
    """Imprime estadísticas de los tiempos de respuesta."""
    if not times:
        print(f"\n{label}: No hay datos")
        return
    
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"Total requests:    {len(times)}")
    print(f"Tiempo promedio:   {statistics.mean(times):.2f}ms")
    print(f"Mediana (P50):     {statistics.median(times):.2f}ms")
    print(f"P95:               {sorted(times)[int(len(times) * 0.95)]:.2f}ms")
    print(f"P99:               {sorted(times)[int(len(times) * 0.99)]:.2f}ms")
    print(f"Mínimo:            {min(times):.2f}ms")
    print(f"Máximo:            {max(times):.2f}ms")
    print(f"Std Dev:           {statistics.stdev(times):.2f}ms")
    
    # Calcular throughput
    total_time = sum(times) / 1000  # Convertir a segundos
    throughput = len(times) / total_time
    print(f"\nThroughput:        {throughput:.2f} req/s")
    print(f"{'='*60}\n")


async def main():
    """Ejecuta todos los benchmarks."""
    print("\n" + "="*60)
    print("BENCHMARK - PDF MICROSERVICE")
    print("="*60)
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    # Test de conectividad
    print("\n🔍 Verificando conectividad...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/pdf/health", timeout=5.0)
            if response.status_code == 200:
                print("  ✓ Servicio disponible")
            else:
                print(f"  ✗ Servicio retornó status {response.status_code}")
                return
    except Exception as e:
        print(f"  ✗ Error de conectividad: {e}")
        return
    
    # Benchmark 1: Requests secuenciales
    seq_times = await sequential_benchmark(num_requests=50)
    print_stats(seq_times, "📊 BENCHMARK SECUENCIAL (50 requests)")
    
    # Benchmark 2: Requests concurrentes (10 concurrencia)
    conc_10_times = await concurrent_benchmark(num_requests=50, concurrency=10)
    print_stats(conc_10_times, "📊 BENCHMARK CONCURRENTE - 10 concurrent")
    
    # Benchmark 3: Requests concurrentes (20 concurrencia)
    conc_20_times = await concurrent_benchmark(num_requests=50, concurrency=20)
    print_stats(conc_20_times, "📊 BENCHMARK CONCURRENTE - 20 concurrent")
    
    # Comparación
    print("\n" + "="*60)
    print("📈 COMPARACIÓN DE RESULTADOS")
    print("="*60)
    print(f"Secuencial:           {statistics.median(seq_times):.2f}ms (P50)")
    print(f"Concurrency 10:       {statistics.median(conc_10_times):.2f}ms (P50)")
    print(f"Concurrency 20:       {statistics.median(conc_20_times):.2f}ms (P50)")
    print("="*60 + "\n")
    
    print("✅ Benchmark completado!\n")


if __name__ == "__main__":
    asyncio.run(main())
