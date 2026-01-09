"""
Test de caché de parsing de fechas
===================================

Verifica que el parsing de fechas se cachea correctamente con @lru_cache.
"""
import pytest
from src.application.utils.date_utils import parse_iso_to_spanish_argentina


def test_date_parsing_cache_hit():
    """Verifica que fechas parseadas se cachean."""
    # Limpiar cache
    parse_iso_to_spanish_argentina.cache_clear()
    
    fecha = "2024-02-20T14:30:00Z"
    
    # Primera llamada
    result1 = parse_iso_to_spanish_argentina(fecha)
    cache_info = parse_iso_to_spanish_argentina.cache_info()
    assert cache_info.hits == 0
    assert cache_info.misses == 1
    
    # Segunda llamada (debe usar cache)
    result2 = parse_iso_to_spanish_argentina(fecha)
    cache_info = parse_iso_to_spanish_argentina.cache_info()
    assert cache_info.hits == 1
    assert cache_info.misses == 1
    
    # Resultados deben ser iguales
    assert result1 == result2


def test_date_parsing_cache_different_dates():
    """Verifica que diferentes fechas se cachean por separado."""
    parse_iso_to_spanish_argentina.cache_clear()
    
    fecha1 = "2024-02-20T14:30:00Z"
    fecha2 = "2024-03-15T10:00:00Z"
    
    result1 = parse_iso_to_spanish_argentina(fecha1)
    result2 = parse_iso_to_spanish_argentina(fecha2)
    
    # Deben ser diferentes
    assert result1 != result2
    
    # Cache hit al volver a llamar
    assert parse_iso_to_spanish_argentina(fecha1) == result1
    assert parse_iso_to_spanish_argentina(fecha2) == result2
    
    cache_info = parse_iso_to_spanish_argentina.cache_info()
    assert cache_info.hits == 2
    assert cache_info.misses == 2


def test_date_parsing_none_handling():
    """Verifica manejo de fechas None."""
    result = parse_iso_to_spanish_argentina(None)
    assert result == ""


def test_date_parsing_formats():
    """Verifica diferentes formatos de fecha."""
    # Datetime con hora
    datetime_result = parse_iso_to_spanish_argentina("2024-02-20T14:30:00Z")
    assert "febrero" in datetime_result
    assert "2024" in datetime_result
    assert "11:30" in datetime_result  # UTC-3
    
    # Solo fecha
    date_result = parse_iso_to_spanish_argentina("2024-03-01")
    assert "marzo" in date_result
    assert "2024" in date_result
    assert "a las" not in date_result  # No debe incluir hora


def test_date_parsing_cache_maxsize():
    """Verifica que el cache respeta el maxsize de 128."""
    parse_iso_to_spanish_argentina.cache_clear()
    
    # Generar 150 fechas únicas
    for i in range(150):
        fecha = f"2024-01-{i % 28 + 1:02d}T{i % 24:02d}:00:00Z"
        parse_iso_to_spanish_argentina(fecha)
    
    cache_info = parse_iso_to_spanish_argentina.cache_info()
    assert cache_info.currsize <= 128, "Cache size should not exceed maxsize"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
