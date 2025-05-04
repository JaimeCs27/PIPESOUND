from customtkinter import *
from tkinter import filedialog, messagebox
import os
import sys
import threading
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from Analizer.ArbimonModule import ArbimonModule


class ArbimonWindow(CTk):
    def __init__(self, master):
        super().__init__()
        self.title("PipeSound")
        self.app_width = 1280
        self.app_height = 720
        self.master = master
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

        self.folder_label = CTkLabel(self, text="Ubicación Carpeta",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF" )
        self.folder_label.place(relx=0.4, rely=0.3, anchor="w")
        self.select_folder_btn = CTkButton(self, text="Seleccionar Carpeta",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=300, height=50,
                                   command=self.select_folder)
        self.select_folder_btn.place(relx=0.2, rely=0.3, anchor="center")

        self.projects = []
        self.sites = []
        self.folder = ""

        self.authenticate()
        self.load_projects()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        project_names = ["Selección de proyectos"] + [item['name'] for item in self.projects]
        self.project_list = CTkComboBox(self, width=200, values=project_names, command=self.selected_project)
        self.project_list.set("Selección de proyectos")
        self.project_list.place(relx= 0.5, rely=0.5)

        # En __init__
        self.sites_frame = CTkScrollableFrame(self, width=300, height=200)
        self.sites_frame.place(relx=0.5, rely=0.6)

        self.site_checkboxes = {}  # Guardará los CheckBox para cada sitio

        self.back_btn = CTkButton(self, text="Volver", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33)
        self.back_btn.place(relx=0, rely=0.1, anchor="w")

        self.start_download_btn = CTkButton(self, text="Empezar Descarga", 
                                   font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=300, height=50,
                                   command=self.start_download)
        self.start_download_btn.place(relx = 0.2, rely= 0.1, anchor="center")

    def get_selected_sites(self):
        selected = []
        for site in self.sites:
            checkbox = self.site_checkboxes[site["id"]]
            if checkbox.get():  # Devuelve True si está marcado
                selected.append(site)
        return selected

    def select_folder(self):
        self.folder = filedialog.askdirectory()
        self.folder_label.configure(text=self.folder)

    def authenticate(self):
        module = ArbimonModule()
        try:
            module.Authenticate()
        except Exception as e:
            print("Error while authenticating with arbimon: " + str(e))

    def on_close(self):
        self.destroy()
        self.master.destroy()

    def download_project_thread(self, sites, folder, project_name):
        module = ArbimonModule()
        module.Authenticate()
        try:
            module.Download_Project(sites, folder, project_name)
            print("Descarga completada")
        except Exception as e:
            print("Error al descargar el proyecto " + project_name + ": " + str(e))

    def start_download(self):
        if self.folder == "":
            print("Carpeta para descarga no seleccionada")
            return
        if self.project_list.get() == "Selección de proyectos":
            print("Debes seleccionar un proyecto")
            return
        sites = self.get_selected_sites()
        if sites == []:
            print("No seleccionaste ningún Site")
            return

        project_name = self.project_list.get()

        # Iniciar la descarga en un hilo
        threading.Thread(target=self.download_project_thread, args=(sites, self.folder, project_name), daemon=True).start()


    def load_projects(self):
        module = ArbimonModule()
        module.Authenticate()
        self.projects = module.Load_projects()

    def load_sites(self, project_id):
        module = ArbimonModule()
        module.Authenticate()
        self.sites = module.Load_Sites(project_id)

    def selected_project(self, name):
        projects = {item["name"]: item for item in self.projects}
        selected = projects[name]
        try:
            self.load_sites(selected['id'])
        except Exception as e:
            print("Error while loading the sites of " + name + ": " + str(e))
        self.update_sites()


    def on_back(self):
        self.master.deiconify()
        self.destroy()

    def update_sites(self):
        # Limpia los checkboxes anteriores
        for widget in self.sites_frame.winfo_children():
            widget.destroy()
        self.site_checkboxes.clear()

        # Crear un checkbox por cada sitio
        for site in self.sites:
            checkbox = CTkCheckBox(self.sites_frame, text=site["name"])
            checkbox.pack(anchor="w", pady=2)
            checkbox.select()  # Esto los marca por defecto
            self.site_checkboxes[site["id"]] = checkbox

        