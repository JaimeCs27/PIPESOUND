from customtkinter import *

class TerminalWindow(CTkToplevel):
    def __init__(self, master, **kw):
        super().__init__(master=master, **kw)
        self.title("Terminal")
        self.geometry("800x400")
        self.configure(fg_color="#272B2B")

        # Crear un marco desplazable para la terminal
        self.scrollable_frame = CTkScrollableFrame(self, width=780, height=350, fg_color="#1E1E1E")
        self.scrollable_frame.pack(pady=10, padx=10)

        # Crear un widget de texto para mostrar los mensajes
        self.text_area = CTkTextbox(self.scrollable_frame, width=760, height=330, fg_color="#1E1E1E", text_color="#FFFFFF", font=("Consolas", 12))
        self.text_area.pack(pady=5, padx=5)
        self.text_area.configure(state="disabled")  # Deshabilitar edición
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def append_text(self, text):
        """Agrega texto a la terminal."""
        def append():
            self.text_area.configure(state="normal")  # Habilitar edición temporalmente
            self.text_area.insert("end", text + "\n")
            self.text_area.see("end")  # Desplazar automáticamente al final
            self.text_area.configure(state="disabled")  # Deshabilitar edición nuevamente
        self.after(0, append)