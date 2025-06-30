from views.root import Root

# --- Paso 4: redirección de print hacia la Terminal ------------------------
import builtins
import datetime
from utils.app_logger import log          # el canal único que creaste

# Guardamos la implementación original de print
_original_print = builtins.print

def gui_print(*args, **kwargs):
    """
    Imprime en la consola *y* envía el mismo texto a la Terminal GUI.
    """
    # 1) Consola normal
    _original_print(*args, **kwargs)

    # 2) TerminalWindow (si Root ya la registró en app_logger)
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    message = " ".join(map(str, args))
    log(f"{timestamp} {message}")

# Sustituimos la función global print por la nueva
builtins.print = gui_print
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app = Root()          # Root registra su Terminal en app_logger.set_logger()
    app.mainloop()
