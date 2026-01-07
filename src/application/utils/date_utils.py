"""
Date Utilities
===============

Utilidades para manejo y formateo de fechas.

Incluye conversión de fechas ISO a formato español
con timezone de Argentina (UTC-3).
"""

from datetime import datetime, timezone, timedelta


MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def parse_iso_to_spanish_argentina(iso_str: str | None) -> str:
    """
    Parsea fecha/datetime ISO a formato español timezone Argentina (UTC-3).
    
    Soporta dos formatos de entrada:
    - Datetime con hora: "2024-02-20T14:30:00Z"
    - Fecha simple: "2024-03-01"
    
    Args:
        iso_str: Fecha en formato ISO 8601 (puede ser None)
        
    Returns:
        Fecha formateada en español, ejemplos:
        - "20 de febrero de 2024 a las 11:30" (para datetime)
        - "1 de marzo de 2024" (para date)
        - "" (si iso_str es None o vacío)
        
    Examples:
        >>> parse_iso_to_spanish_argentina("2024-02-20T14:30:00Z")
        "20 de febrero de 2024 a las 11:30"
        
        >>> parse_iso_to_spanish_argentina("2024-03-01")
        "1 de marzo de 2024"
        
        >>> parse_iso_to_spanish_argentina(None)
        ""
    """
    if not iso_str:
        return ""
    
    # Parsear fecha ISO (soporta con o sin hora)
    try:
        if "T" in iso_str:
            # Datetime con hora
            if iso_str.endswith("Z"):
                dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            else:
                dt = datetime.fromisoformat(iso_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Solo fecha
            dt = datetime.strptime(iso_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        # Si falla el parseo, retornar el string original
        return iso_str
    
    # Convertir a timezone Argentina (UTC-3)
    arg_tz = timezone(timedelta(hours=-3))
    dt_arg = dt.astimezone(arg_tz)
    
    # Formatear en español
    day = dt_arg.day
    month = MESES_ES[dt_arg.month - 1]
    year = dt_arg.year
    
    # Si tiene hora, incluirla en el formato
    if "T" in iso_str:
        hour = dt_arg.hour
        minute = dt_arg.minute
        return f"{day} de {month} de {year} a las {hour:02d}:{minute:02d}"
    else:
        return f"{day} de {month} de {year}"
