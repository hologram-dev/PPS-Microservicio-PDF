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
# IMPORTANTE: Actualiza BASE_URL con el puerto correcto donde corre tu servicio
# - Si usas docker: http://localhost:9000 (puerto mapeado en docker-compose.yml)
# - Si usas local: http://localhost:8000
BASE_URL = "http://localhost:9000"  # ⚠️ Cambiar según tu configuración

PAYLOAD_POSTULACION = {
  "estudiante": {
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "40123456",
    "email": "juan.perez@mail.universidad.edu.ar",
    "cuil": "20-40123456-8",
    "fecha_nacimiento": "2000-05-15",
    "tipo_dni": "DNI"
  },
  "universidad": {
    "nombre": "Universidad Nacional de La Plata",
    "direccion": "Avenida 7 #776",
    "codigo_postal": 1900,
    "correo": "academica@presi.unlp.edu.ar",
    "telefono": "+54 221 421-1234"
  },
  "carrera": {
    "nombre": "Ingeniería en Informática",
    "codigo": "INF-2020",
    "descripcion": "Carrera de grado orientada al desarrollo de software y sistemas.",
    "plan_estudios": "Plan de estudios 2020"
  },
  "empresa": {
    "nombre": "MercadoLibre S.R.L.",
    "direccion": "Arieta 4865, Piso 14",
    "codigo_postal": 1430,
    "telefono": "+54 11 4640-8000",
    "codigo": 789
  },
  "proyecto": {
    "nombre": "Migración a Microservicios - Plataforma de Pagos",
    "fecha_inicio": "2024-02-01",
    "descripcion": "Refactorización del monolito principal de pagos hacia una arquitectura de microservicios.",
    "numero": 101,
    "estado": "En Progreso",
    "fecha_fin": "2024-12-15"
  },
  "puesto": {
    "nombre": "Desarrollador Backend Trainee",
    "descripcion": "Apoyar en el desarrollo de APIs y servicios para el nuevo módulo de pagos.",
    "codigo": 15,
    "horas_dedicadas": 20
  },
  "postulacion": {
    "numero": 5001,
    "fecha": "2024-01-20",
    "cantidad_materias_aprobadas": 28,
    "cantidad_materias_regulares": 5,
    "estado": "Pendiente"
  }
}

PAYLOAD_CONTRATO = {
  "estudiante": {
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "40123456",
    "email": "juan.perez@mail.universidad.edu.ar",
    "cuil": "20-40123456-8",
    "fecha_nacimiento": "2000-05-15",
    "tipo_dni": "DNI"
  },
  "universidad": {
    "nombre": "Universidad Nacional de La Plata",
    "direccion": "Avenida 7 #776",
    "codigo_postal": "1900",
    "correo": "academica@presi.unlp.edu.ar",
    "telefono": "+54 221 421-1234"
  },
  "carrera": {
    "nombre": "Ingeniería en Informática",
    "codigo": "INF-2020",
    "descripcion": "Carrera de grado orientada al desarrollo de software y sistemas.",
    "plan_estudios": "Plan de estudios 2020"
  },
  "empresa": {
    "nombre": "MercadoLibre S.R.L.",
    "direccion": "Arieta 4865, Piso 14",
    "codigo_postal": 5550,
    "correo": "rrhh@mercadolibre.com",
    "telefono": "+54 11 4640-8000",
    "codigo": 789
  },
  "proyecto": {
    "nombre": "Migración a Microservicios - Plataforma de Pagos",
    "fecha_inicio": "2024-02-01",
    "descripcion": "Refactorización del monolito principal de pagos hacia una arquitectura de microservicios.",
    "numero": 101,
    "estado": "En Progreso",
    "fecha_fin": "2024-12-15"
  },
  "puesto": {
    "nombre": "Desarrollador Backend Trainee",
    "descripcion": "Apoyar en el desarrollo de APIs y servicios para el nuevo módulo de pagos.",
    "codigo": "12341",
    "horas_dedicadas": 20
  },
  "postulacion": {
    "numero": 5001,
    "fecha": "2024-01-20",
    "cantidad_materias_aprobadas": 28,
    "cantidad_materias_regulares": 5,
    "estado": "Aprobada"
  },
  "contrato": {
    "numero": 245,
    "fecha_inicio": "2024-03-01",
    "fecha_fin": "2024-12-31",
    "fecha_emision": "2024-02-25",
    "estado": "Activo"
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
        payload["postulacion"]["numero"] = random.randint(400000, 499999)  # Integer, no string
        
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
        payload["contrato"]["numero"] = random.randint(500000, 599999)  # Integer, no string
        
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
        payload["postulacion"]["numero"] = random.randint(100000, 999999)  # Integer para carga pesada
        
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
