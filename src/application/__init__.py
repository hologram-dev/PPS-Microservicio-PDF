# ================================
# Application Layer
# ================================
# Esta capa orquesta los casos de uso de la aplicación.
# Depende SOLO del dominio (entities, interfaces, etc.)
# NO conoce FastAPI ni ReportLab.
#
# Componentes:
# - use_cases: Acciones del sistema (casos de uso)
# - dto: Data Transfer Objects
#
# NOTA: En Clean Architecture ortodoxo, los casos de uso (use_cases)
# SON los servicios de aplicación. No necesitamos una capa de "services".
# ================================
