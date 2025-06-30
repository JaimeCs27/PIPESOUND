"""
Pequeño logger global que reenvía mensajes a la terminal de la app.
Si aún no hay GUI, cae en print() normal.
"""
from typing import Callable

_log_func: Callable[[str], None] = print      # por defecto a consola

def set_logger(func: Callable[[str], None]) -> None:
    """Root registra aquí su función append_text()."""
    global _log_func
    _log_func = func

def log(msg: str) -> None:
    """Llamar desde cualquier parte del proyecto."""
    _log_func(msg)
