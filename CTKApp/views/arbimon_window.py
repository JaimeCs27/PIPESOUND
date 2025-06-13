from customtkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
import sys
import threading
import shutil
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from controllers.arbimonModule import ArbimonModule

class ArbimonWindow(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._load_images()
        self.btn_setup()
        self.label_setup()

        self.controller = controller
        self.projects = []
        self.sites = []
        self.folder = ""

        
        self.selection_setup()    
        self.loading_setup()

        self.site_checkboxes = {}  # Guardará los CheckBox para cada sitio

    

    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None


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

    def load_up(self):
        self.btn_logout.configure(state="normal")
        self.log_in.configure(state="disabled")
        self.load_projects()
        self.selection_setup()

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
        self.back_btn = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.back_btn.place(relx=0.02, rely=0.05, anchor="w")
        self.select_folder_btn = CTkButton(self, text="Seleccionar Carpeta",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=200, height=50,
                                   command=self.select_folder)
        self.select_folder_btn.place(relx=0.05, rely=0.2, anchor="w")
        self.log_in = CTkButton(self, text="Log In",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=100, height=35, command=self.load_up, state="disabled")
        self.log_in.place(relx=0.05, rely=0.12, anchor="w")
        self.btn_logout = CTkButton(self, text="Log Out", 
                                    font=("Inter", 18), fg_color="#AA4545", 
                                    hover_color="#000000", width=100, height=35 ,
                                    command=self.log_out
                                    )
        self.btn_logout.place(relx=0.17, rely=0.12, anchor="center")
        if not os.path.exists(".rfcx_credentials"):
            self.btn_logout.configure(state="disabled")
            self.log_in.configure(state="normal")

    def log_out(self):
        credentials = ".rfcx_credentials"
        if os.path.exists(credentials):
            os.remove(credentials)
            print("Logged Out")
            self.projects = []
            self.sites = []
            self.folder = ""
            self.site_checkboxes = {}
            self.project_list.configure(values=["Need to log in"])
            self.project_list.set("Need to log in")
            self.btn_logout.configure(state="disabled")
            self.log_in.configure(state="normal")
        else:
            print("You are not logged in")

    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")

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

    def download_project_thread(self, sites, folder, project_name):
        module = ArbimonModule()
        module.Authenticate()
        try:
            module.Download_Project(sites, folder, project_name)
            print("Download completed for project: " + project_name)
            self.after(0, lambda: messagebox.showinfo("Success", f"Download of project '{project_name}' completed."))
        except Exception as e:
            print("Error downloading project " + project_name + ": " + str(e))
            self.last_error = e
            self.after(0, lambda: self.show_retry_dialog(self.last_error, sites, folder, project_name))
        finally:
            self.after(0, self.hide_progress_bar)

    def show_retry_dialog(self, error, sites, folder, project_name):
        retry = messagebox.askretrycancel(
            "Error en la descarga",
            f"Ocurrió un error durante la descarga:\n\n{str(error)}\n\n"
            "¿Desea reintentar desde el último archivo descargado?\n"
            "(Cancelar borrará los archivos parcialmente descargados)",
            icon='error'
        )
        
        if retry:
            # Retry the download
            self.progress_bar.place(relx=0.05, rely=0.78, anchor="w")
            self.progress_bar.start()
            threading.Thread(
                target=self.download_project_thread,
                args=(sites, folder, project_name),
                daemon=True
            ).start()
        else:
            # Clean up partial downloads
            self.cleanup_partial_downloads(folder, project_name)

    def cleanup_partial_downloads(self, folder, project_name):
        try:
            target_path = os.path.join(folder, project_name)
            temp_dir = os.path.join(folder, '.temp_downloads')
            
            # Primero eliminar archivos temporales si existen
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if filename.startswith(project_name):
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)  # Borrar archivo
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)  # Borrar directorio
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

            # Luego borrar el directorio principal (si existe)
            if os.path.exists(target_path):
                try:
                    shutil.rmtree(target_path)  # Esto borra recursivamente
                except PermissionError:
                    # Intento alternativo para liberar archivos bloqueados
                    import time
                    time.sleep(1)  # Esperar 1 segundo
                    shutil.rmtree(target_path, ignore_errors=True)

            messagebox.showinfo("Operation cancelled", 
                            "Partially downloaded files have been deleted.")
            
        except Exception as e:
            messagebox.showerror("Error cleaning up", 
                            f"Could not delete all files:\n{str(e)}")

    def hide_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.place_forget()  # Oculta la barra completamente

    def start_download(self):
        if self.folder == "":
            print("Download folder not selected")
            return
        if self.project_list.get() == "Select a project":
            print("You must select a project")
            return
        sites = self.get_selected_sites()
        if sites == []:
            print("No sites selected")
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
        self.controller.show_frame("PipeSoundWelcome")

    def clean_checkboxes(self):
        for site, checkbox in self.site_checkboxes.items():
            #print("destruyendo widget")
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

        