"""Errores de dominio mostrables al usuario."""


class SmartSupportError(Exception):
    """Error controlado de la aplicacion."""


class ConfigurationError(SmartSupportError):
    """Configuracion local incompleta o invalida."""


class ServiceError(SmartSupportError):
    """Falla de un servicio externo."""


class ValidationError(SmartSupportError):
    """Entrada del usuario no valida."""

