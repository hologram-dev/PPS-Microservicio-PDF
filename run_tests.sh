#!/bin/bash
# run_tests.sh - Script helper para ejecutar tests

echo "🧪 Running PDF Microservice Tests"
echo "=================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: No estás en el directorio raíz del proyecto"
    echo "   Ejecuta: cd /mnt/h/microservicio\ PDF/Microservicio-PDF"
    exit 1
fi

# Configurar PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Opción 1: Tests unitarios
if [ "$1" == "unit" ]; then
    echo "Running unit tests..."
    pytest tests/unit tests/integration -v

# Opción 2: Tests con coverage
elif [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    pytest tests/unit tests/integration -v --cov=src --cov-report=html
    echo "✅ Coverage report: htmlcov/index.html"

# Opción 3: Load testing
elif [ "$1" == "load" ]; then
    echo "Running load tests with Locust..."
    locust -f tests/load/locustfile.py --host http://localhost:8000

# Opción 4: Benchmark
elif [ "$1" == "benchmark" ]; then
    echo "Running benchmark..."
    python tests/benchmark/benchmark.py

# Opción 5: Instalar dependencias
elif [ "$1" == "install" ]; then
    echo "Installing test dependencies..."
    pip install -r requirements-test.txt
    echo "✅ Dependencies installed!"

else
    echo "Uso: ./run_tests.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install   - Instalar dependencias de testing"
    echo "  unit      - Ejecutar tests unitarios"
    echo "  coverage  - Tests con coverage report"
    echo "  load      - Load testing con Locust"
    echo "  benchmark - Ejecutar benchmark de performance"
fi
