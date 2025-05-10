from customtkinter import *
from tkinter import filedialog, messagebox

import sys
import threading
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from Analizer.ArbimonModule import ArbimonModule


class ArbimonWindow(CTk):
    def __init__(self, master):
        super().__init__()
        self.window_setup()
        self.btn_setup()
        self.label_setup()

        self.master = master
        self.projects = []
        self.sites = []
        self.folder = ""

        self.authenticate()
        self.load_projects()
        self.selection_setup()
        self.loading_setup()

        self.site_checkboxes = {}  # Guardará los CheckBox para cada sitio

    def selection_setup(self):
        project_names = ["Selección de proyectos"] + [item['name'] for item in self.projects]
        self.project_list = CTkComboBox(self, width=250, values=project_names, command=self.selected_project, font=("Inter", 18), dropdown_font=("Inter", 15))
        self.project_list.set("Selección de proyectos")
        self.project_list.place(relx= 0.05, rely=0.29, anchor='w')

        # En __init__
        self.sites_frame = CTkScrollableFrame(self, width=300, height=200, fg_color="#131616")
        self.sites_frame.place(relx=0.05, rely=0.4, anchor='nw')

    def loading_setup(self):
        self.progress_bar = CTkProgressBar(self, width=300)
        
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.stop()

    def window_setup(self):
        self.title("PipeSound")
        self.app_width = 1280
        self.app_height = 720
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        x = (self.winfo_screenwidth() // 2) - (self.app_width // 2)
        y = (self.winfo_screenheight() // 2) - (self.app_height // 2)
        self.geometry(f"{self.app_width}x{self.app_height}+{x}+{y}")
        self.configure(fg_color="#272B2B")

    def label_setup(self):
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
        self.folder_label.place(relx=0.25, rely=0.2, anchor="w")
        self.sites_label = CTkLabel(self, text="Lista de Sites",fg_color="transparent",
                                    font=("Inter", 18), text_color="#FFFFFF" )
        self.sites_label.place(relx=0.05, rely=0.35, anchor="w")

    def btn_setup(self):
        self.start_download_btn = CTkButton(self, text="Empezar Descarga", 
                                   font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=300, height=50,
                                   command=self.start_download)
        self.start_download_btn.place(relx = 0.05, rely= 0.85, anchor="w")
        self.back_btn = CTkButton(self, text="Volver", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33)
        self.back_btn.place(relx=0.02, rely=0.05, anchor="w")
        self.select_folder_btn = CTkButton(self, text="Seleccionar Carpeta",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=200, height=50,
                                   command=self.select_folder)
        self.select_folder_btn.place(relx=0.05, rely=0.2, anchor="w")


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
            self.after(0, lambda: messagebox.showinfo("Éxito", f"Descarga del proyecto '{project_name}' completada."))
        except Exception as e:
            print("Error al descargar el proyecto " + project_name + ": " + str(e))
            self.after(0, lambda: messagebox.showerror("Error", f"Fallo al descargar '{project_name}': {e}"))
        finally:
            self.after(0, self.hide_progress_bar)

    def hide_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.place_forget()  # Oculta la barra completamente

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
        self.progress_bar.place(relx=0.05, rely=0.78, anchor="w")
        self.progress_bar.start()
        self.progress_bar.update()

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
        if name == 'Selección de proyectos':
            self.clean_checkboxes()
            return
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

    def clean_checkboxes(self):
        for site, checkbox in self.site_checkboxes.items():
            print("destruyendo widget")
            checkbox.destroy()
        self.sites_frame.update()  # Forzar refresco
        self.site_checkboxes.clear()

    def update_sites(self):
        self.clean_checkboxes()

        # Crear un checkbox por cada sitio
        for site in self.sites:
            checkbox = CTkCheckBox(self.sites_frame, text=site["name"])
            checkbox.pack(anchor="w", pady=2)
            checkbox.select()  # Esto los marca por defecto
            self.site_checkboxes[site["id"]] = checkbox

        