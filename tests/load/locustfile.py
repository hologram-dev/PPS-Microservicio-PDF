"""
Load Testing con Locust - PDF Microservice
==========================================

Script de stress testing para evaluar performance del microservicio PDF.

Uso:
    # Modo interfaz web (recomendado)
    locust -f tests/load/locustfile.py --host http://localhost:8001
    
    # Modo headless (CI/CD)
    locust -f tests/load/locustfile.py --host http://localhost:8001 \\
           -u 50 -r 5 --run-time 5m --headless

Parámetros:
    -u: Número de usuarios concurrentes
    -r: Rate de spawn (usuarios/segundo)
    --run-time: Duración del test
"""
from locust import HttpUser, task, between, events
import json
import random


# Payload de ejemplo para generación de PDF
PAYLOAD_POSTULACION = {
    "estudiante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan.perez@example.com",
        "cuil": "20-12345678-9",
        "fecha_nacimiento": "1990-01-01",
        "tipo_dni": "DNI"
    },
    "universidad": {
        "nombre": "Universidad Tecnológica Nacional",
        "direccion": "Av. Independencia 850",
        "codigo_postal": "5000",
        "correo": "info@utn.edu.ar",
        "telefono": "351-4520800"
    },
    "carrera": {
        "nombre": "Ingeniería en Sistemas de Información",
        "codigo": "K08",
        "descripcion": "Carrera de grado en Ingeniería",
        "plan_estudios": "2008"
    },
    "empresa": {
        "nombre": "Tech Solutions SA",
        "direccion": "Calle Empresarial 456",
        "codigo_postal": "5001",
        "telefono": "351-9876543",
        "codigo": "EMP001"
    },
    "proyecto": {
        "nombre": "Sistema de Gestión Web",
        "fecha_inicio": "2024-01-15",
        "descripcion": "Desarrollo de plataforma web integral",
        "numero": "PRY2024001",
        "estado": "activo",
        "fecha_fin": "2024-12-31"
    },
    "puesto": {
        "nombre": "Desarrollador Full Stack",
        "descripcion": "Desarrollo de frontend y backend",
        "codigo": "DEV-FS-001",
        "horas_dedicadas": 40
    },
    "postulacion": {
        "numero": "POST2024001",
        "fecha": "2024-01-10",
        "cantidad_materias_aprobadas": 28,
        "cantidad_materias_regulares": 4,
        "estado": "aprobada"
    }
}


PAYLOAD_CONTRATO = {
    **PAYLOAD_POSTULACION,
    "contrato": {
        "numero": "CONT2024001",
        "fecha_inicio": "2024-02-01",
        "fecha_fin": "2024-12-31",
        "fecha_emision": "2024-01-20",
        "estado": "vigente"
    }
}


class PDFUser(HttpUser):
    """
    Usuario simulado que genera PDFs.
    
    Simula un usuario real que alterna entre:
    - Generar PDFs de postulación
    - Generar PDFs de contrato
    - Verificar health del servicio
    """
    
    # Tiempo de espera entre requests (1-3 segundos)
    wait_time = between(1, 3)
    
    @task(3)  # Peso 3: más frecuente
    def generar_pdf_postulacion(self):
        """Genera PDF de comprobante de postulación."""
        # Variar algunos datos para simular requests diferentes
        payload = PAYLOAD_POSTULACION.copy()
        payload["estudiante"]["nombre"] = random.choice(["Juan", "María", "Carlos", "Ana"])
        payload["postulacion"]["numero"] = f"POST2024{random.randint(1, 9999):04d}"
        
        with self.client.post(
            "/api/v1/pdf/generate/comprobante_postulacion",
            json=payload,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                # Verificar que es un PDF válido
                if response.headers.get("Content-Type") == "application/pdf":
                    response.success()
                else:
                    response.failure("Response is not a PDF")
            elif response.status_code == 429:
                # Rate limit es esperado bajo alta carga
                response.success()
            else:
                response.failure(f"Got unexpected status {response.status_code}")
    
    @task(2)  # Peso 2: menos frecuente
    def generar_pdf_contrato(self):
        """Genera PDF de comprobante de contrato."""
        payload = PAYLOAD_CONTRATO.copy()
        payload["estudiante"]["nombre"] = random.choice(["Pedro", "Lucía", "Diego", "Sofía"])
        payload["contrato"]["numero"] = f"CONT2024{random.randint(1, 9999):04d}"
        
        with self.client.post(
            "/api/v1/pdf/generate/comprobante_contrato",
            json=payload,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                if response.headers.get("Content-Type") == "application/pdf":
                    response.success()
                else:
                    response.failure("Response is not a PDF")
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Got unexpected status {response.status_code}")
    
    @task(1)  # Peso 1: ocasional
    def health_check(self):
        """Verifica el health del servicio."""
        with self.client.get(
            "/api/v1/pdf/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Service is not healthy")
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Health check failed with {response.status_code}")


class HeavyLoadUser(HttpUser):
    """
    Usuario de carga pesada.
    
    Simula carga máxima sin esperas entre requests.
    Útil para stress testing extremo.
    """
    
    wait_time = between(0.1, 0.5)  # Casi sin espera
    
    @task
    def rapid_fire_pdf_generation(self):
        """Genera PDFs en ráfaga rápida."""
        payload = PAYLOAD_POSTULACION.copy()
        payload["postulacion"]["numero"] = f"LOAD{random.randint(1, 99999):05d}"
        
        self.client.post(
            "/api/v1/pdf/generate/comprobante_postulacion",
            json=payload,
            catch_response=True
        )


# Event listeners para estadísticas personalizadas
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Se ejecuta al iniciar el test."""
    print("\n" + "="*60)
    print("INICIANDO LOAD TEST - PDF MICROSERVICE")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: Configurado en CLI o UI")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Se ejecuta al finalizar el test."""
    print("\n" + "="*60)
    print("LOAD TEST FINALIZADO")
    print("="*60)
    
    stats = environment.stats
    print(f"\nRequests totales: {stats.total.num_requests}")
    print(f"Failures: {stats.total.num_failures}")
    print(f"RPS promedio: {stats.total.current_rps:.2f}")
    print(f"Response time promedio: {stats.total.avg_response_time:.2f}ms")
    print(f"Response time mediana: {stats.total.median_response_time:.2f}ms")
    print(f"Response time P95: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"Response time P99: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print("="*60 + "\n")
