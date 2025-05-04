from customtkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
import os
import sys
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from Analizer.progress import load_last_processed_data, reset_progress
from ArbimonWindow import ArbimonWindow

class PipeSoundWelcome(CTk):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        # Configuración de la ventana (mismo tamaño que tu ventana principal)
        self.title("PipeSound")
        self.app_width = 1280
        self.app_height = 720
        x = (self.winfo_screenwidth() // 2) - (self.app_width // 2)
        y = (self.winfo_screenheight() // 2) - (self.app_height // 2)
        self.geometry(f"{self.app_width}x{self.app_height}+{x}+{y}")
        self.configure(fg_color="#272B2B")
        
        # Logo PipeSound (igual que en tu ventana principal)
        self.label_pipe = CTkLabel(self, text="Pipe", text_color="#FFFFFF", 
                                 fg_color="transparent", font=("Inter", 30), 
                                 anchor="w", width=67, height=34)
        self.label_pipe.place(x=1055, y=23)
        
        self.label_sound = CTkLabel(self, text="Sound", text_color="#63C132", 
                                  fg_color="transparent", font=("Inter", 30), 
                                  anchor="w", width=112, height=34)
        self.label_sound.place(x=1119, y=23)
        
        # Título Bienvenida
        self.label_bienvenida = CTkLabel(self, text="Bienvenido", text_color="#FFFFFF", 
                                       fg_color="transparent", font=("Inter", 32))
        self.label_bienvenida.place(relx=0.5, rely=0.2, anchor="center")
        
        # Subtítulo
        self.label_subtitulo = CTkLabel(self, 
                                      text="Para comenzar por favor seleccione la opción de su preferencia", 
                                      text_color="#FFFFFF", fg_color="transparent", 
                                      font=("Inter", 20))
        self.label_subtitulo.place(relx=0.5, rely=0.3, anchor="center")
        
        # Sección ARBIMON
        #self.label_arbimon = CTkLabel(self, text="ARBIMON", text_color="#FFFFFF", 
        #                             fg_color="transparent", font=("Inter", 24, "bold"))
        #self.label_arbimon.place(relx=0.5, rely=0.4, anchor="center")
        
        # Botón ARBIMON (sin implementar)
        self.btn_arbimon = CTkButton(self, text="Descargar desde ARBIMON", 
                                    font=("Inter", 18), fg_color="#63C132", 
                                    hover_color="#63C132", width=300, height=50 ,
                                    command=self.seleccionar_proyecto_arbimon
                                    )
        self.btn_arbimon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Botón Carpeta Local
        self.btn_carpeta = CTkButton(self, text="Subir de carpeta local", 
                                   font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=300, height=50,
                                   command=self.seleccionar_carpeta)
        self.btn_carpeta.place(relx=0.5, rely=0.6, anchor="center")

        self.last_file = load_last_processed_data()
        if self.last_file:
            self.reanudarProgresoPopUp(f"El programa fue interrumpido repentinamente, se encontró progreso previo en '{self.last_file['root']}'. ¿Desea continuar desde allí?")
        
        
        # Créditos
        #self.label_creditos = CTkLabel(self, text="En alianza con:", 
        #                              text_color="#FFFFFF", fg_color="transparent", 
        #                              font=("Inter", 16))
        #self.label_creditos.place(relx=0.5, rely=0.85, anchor="center")
        
        # Aquí podrías añadir logos de aliados si los tienes
    
    def seleccionar_proyecto_arbimon(self):
        self.withdraw()
        arbimonWindow = ArbimonWindow(self)
        arbimonWindow.mainloop()

    
    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            if self.contiene_audio(carpeta):
                if self.callback:  # Usa el callback si existe
                    self.callback(carpeta)
            else:
                messagebox.showerror("Error", "La carpeta no contiene archivos de audio válidos (.wav)")
    
    def contiene_audio(self, ruta):
        for root, dirs, files in os.walk(ruta):
            for file in files:
                if file.lower().endswith('.wav') or file.lower().endswith('.flac'): #agregando .flac
                    return True
        return False
    

    def iniciarReanudarProgreso(self):
        if self.callback:
            self.callback(self.last_file['root'])

    def reanudarProgresoPopUp(self, message):
        popup = CTkToplevel(self)
        popup.title("Recuperar progreso")
        popup.configure(fg_color="#272B2B")
        popup_width = 400  # Un poco más ancho para acomodar los dos botones
        popup_height = 220
        x = (self.winfo_screenwidth() // 2) - (popup_width // 2)
        y = (self.winfo_screenheight() // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.resizable(False, False)  # Evitar que el usuario redimensione
        
        # Configurar el mensaje
        label = CTkLabel(popup, 
                        text=message, 
                        text_color="#FFFFFF", 
                        font=("Inter", 14),  # Tamaño más pequeño para mensajes largos
                        wraplength=350,  # Ajustar texto largo
                        justify="center")
        label.pack(pady=20, padx=10)
        
        # Frame para contener los botones
        button_frame = CTkFrame(popup, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Botón Sí
        btn_yes = CTkButton(button_frame, 
                        text="Sí", 
                        font=("Inter", 16),
                        width=100,
                        fg_color="#2E8B57", 
                        hover_color="#3CB371",
                        command=lambda: [self.callback(self.last_file['root'])])
        btn_yes.pack(side="left", padx=10)


        
        # Botón No
        btn_no = CTkButton(button_frame, 
                        text="No", 
                        font=("Inter", 16),
                        width=100,
                        fg_color="#B22222",
                        hover_color="#CD5C5C",
                        command=lambda: [reset_progress(), popup.destroy()])
        btn_no.pack(side="left", padx=10)
        
        popup.focus_set()
        popup.grab_set()
        popup.transient(self)  
        

