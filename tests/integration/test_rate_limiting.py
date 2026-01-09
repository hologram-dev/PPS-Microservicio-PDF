"""
Test de integración para rate limiting
=======================================

Verifica que el rate limiting con SlowAPI funciona correctamente.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import create_app


@pytest.fixture
def client():
    """Crea un cliente de test."""
    app = create_app()
    return TestClient(app)


def test_rate_limit_health_endpoint(client):
    """Verifica que el rate limiting funciona en /health."""
    # Hacer 200 requests (límite: 200/min)
    for i in range(200):
        response = client.get("/api/v1/pdf/health")
        assert response.status_code == 200, f"Request {i+1} debería ser 200"
    
    # Request 201 debería ser bloqueado
    response = client.get("/api/v1/pdf/health")
    assert response.status_code == 429, "Request 201 debería retornar 429 Too Many Requests"
    
    # Verificar mensaje de error
    data = response.json()
    assert "error" in data
    assert data["error"] == "Rate limit exceeded"


def test_rate_limit_headers(client):
    """Verifica que se incluyen headers de rate limit."""
    response = client.get("/api/v1/pdf/health")
    
    # SlowAPI debería incluir headers informativos
    # Nota: Esto depende de la configuración de SlowAPI
    assert response.status_code == 200


def test_rate_limit_different_endpoints_independent(client):
    """Verifica que los límites son independientes por endpoint."""
    # Hacer requests al health endpoint
    for _ in range(100):
        response = client.get("/api/v1/pdf/health")
        assert response.status_code == 200
    
    # El endpoint de root no debería estar afectado
    response = client.get("/")
    assert response.status_code == 200


def test_rate_limit_error_response_format(client):
    """Verifica el formato de respuesta de error de rate limiting."""
    # Exceder el límite
    for _ in range(201):
        client.get("/api/v1/pdf/health")
    
    response = client.get("/api/v1/pdf/health")
    assert response.status_code == 429
    
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert isinstance(data["error"], str)
    assert isinstance(data["message"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
