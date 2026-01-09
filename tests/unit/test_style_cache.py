"""
Test de caché de estilos PDF
=============================

Verifica que los estilos se cacheen correctamente con @lru_cache.
"""
import pytest
from src.infrastructure.pdf.reportlab_generator import ReportLabGenerator
from src.domain.value_objects import PDFStyle


def test_style_cache_hit():
    """Verifica que estilos se cachean correctamente."""
    generator = ReportLabGenerator()
    style = PDFStyle.default()
    
    # Primera llamada: cache miss
    styles1 = generator._create_styles(style)
    
    # Segunda llamada: cache hit (debe ser la misma instancia)
    styles2 = generator._create_styles(style)
    
    assert styles1 is styles2, "Styles should be cached and return same instance"


def test_style_cache_different_styles():
    """Verifica que diferentes estilos se cachean por separado."""
    generator = ReportLabGenerator()
    
    default_style = PDFStyle.default()
    professional_style = PDFStyle.professional()
    
    styles_default = generator._create_styles(default_style)
    styles_professional = generator._create_styles(professional_style)
    
    # Deben ser instancias diferentes
    assert styles_default is not styles_professional
    
    # Verificar cache hit para cada uno
    assert generator._create_styles(default_style) is styles_default
    assert generator._create_styles(professional_style) is styles_professional


def test_style_cache_info():
    """Verifica las estadísticas del cache."""
    generator = ReportLabGenerator()
    
    # Limpiar cache
    generator._create_styles.cache_clear()
    
    style = PDFStyle.default()
    
    # Primera llamada
    generator._create_styles(style)
    cache_info = generator._create_styles.cache_info()
    assert cache_info.hits == 0
    assert cache_info.misses == 1
    
    # Segunda llamada (cache hit)
    generator._create_styles(style)
    cache_info = generator._create_styles.cache_info()
    assert cache_info.hits == 1
    assert cache_info.misses == 1


def test_style_cache_maxsize():
    """Verifica que el cache respeta el maxsize."""
    generator = ReportLabGenerator()
    generator._create_styles.cache_clear()
    
    # Crear más de 16 estilos únicos (maxsize=16)
    # Esto debería causar eviction de los primeros estilos
    from src.domain.value_objects import ColorConfig, FontConfig, MarginConfig
    
    styles_list = []
    for i in range(20):
        custom_color = ColorConfig(primary=f"#{i:02x}0000")  # Diferentes colores
        custom_style = PDFStyle(colors=custom_color)
        styles_list.append(generator._create_styles(custom_style))
    
    cache_info = generator._create_styles.cache_info()
    # Debe haber evictions debido al maxsize
    assert cache_info.currsize <= 16, "Cache size should not exceed maxsize"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
