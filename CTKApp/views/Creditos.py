from customtkinter import *
from PIL import Image
import sys
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))


class Creditos(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._load_images()
        self.label_setup()
        self.btn_setup()

    def label_setup(self):
        self.label_pipe = CTkLabel(self, text="Pipe", text_color="#FFFFFF", 
                                 fg_color="transparent", font=("Inter", 45), 
                                 anchor="w", height=34)
        self.label_pipe.place(relx=0.485, rely=0.2, anchor="e")
        
        self.label_sound = CTkLabel(self, text="Sound", text_color="#63C132", 
                                  fg_color="transparent", font=("Inter", 45), 
                                  anchor="w", height=34)
        self.label_sound.place(relx=0.485, rely=0.2, anchor="w")
        label = CTkLabel(self, text="Desarrollado por:\n\nJaime Cabezas Segura jaimecabezassegura@gmail.com\nSebastian Lopez Villavicencio Selopez@estudiantec.cr\nJose Ramirez Castillo jaramirez@estudiantec.cr\nNatasha Calderón Rojas nacalderon@estudiantec.cr\n\nEn alianza con:\n\nUNED\nLaboratorio de Investigación e Innovación Tecnológica",
                         fg_color="transparent", font=("Inter", 25), text_color="#FFFFFF")
        label.place(relx=0.5, rely=0.5, anchor="center")

    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None

    def btn_setup(self):
        self.back_btn = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.back_btn.place(relx=0.02, rely=0.05, anchor="w")

    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")