from customtkinter import *
from PIL import Image
import sys
from os import path, walk
import threading
from bienvenida import PipeSoundWelcome
# Agrega la carpeta superior al path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from Analizer.Analizer import *
from Analizer.progress import load_last_processed_data, save_last_processed_data, reset_progress, PROGRESS_FILE, analize

# Global variables
STOP = False
SELECTED_FOLDER = None
app = None  
welcome_app = None
INDICES = ['Acoustic_Complexity_Index', 'Acoustic_Diversity_Index',
               'Acoustic_Evenness_Index', 'Bio_acoustic_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy',
               'NB_peaks', 'Temporal_Entropy', 'Wave_Signal_To_Noise_Ratio']

class MainApplication(CTk):
    def __init__(self, folder_path):
        super().__init__()
        self.SELECTED_FOLDER = folder_path
        self.title("PipeSound Analyzer")
        self._setup_main_window()
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.last_file = load_last_processed_data()

    def _setup_main_window(self):
        self.width = 1280
        self.height = 720
        x = (self.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.winfo_screenheight() // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.configure(fg_color="#272B2B")

    def _create_widgets(self):
        # Load images
        self._load_images()
        
        # Create all UI elements
        self._create_buttons()
        self._create_labels()
        self._create_progress_bar()
        self._create_checkboxes()
        
    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open("icons/Arrow.png"))
            self.img_run = CTkImage(Image.open("icons/Run.png"))
            self.img_stop = CTkImage(Image.open("icons/Stop.png"))
        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None
            self.img_run = None
            self.img_stop = None

    def _create_buttons(self):
        # Back button
        self.btn_back = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.btn_back.place(x=51, y=19)

        # Run button
        self.btn_run = CTkButton(self, text="Correr", font=("Inter", 36), 
                               fg_color="#63C132", hover_color="#63C132", 
                               command=self.run_indices, width=448, height=49, 
                               image=self.img_run)
        self.btn_run.place(x=79, y=627)

        # Stop button
        self.btn_stop = CTkButton(self, text="Detener", font=("Inter", 36), 
                                fg_color="#F21D1D", hover_color="#F21D1D", 
                                command=self.stop_analysis, width=448, height=49, 
                                image=self.img_stop)
        self.btn_stop.place(x=659, y=627)

    def _create_labels(self):
        # PipeSound label
        CTkLabel(self, text="Pipe", text_color="#FFFFFF", fg_color="transparent", 
                font=("Inter", 30), anchor="w", width=67, height=34).place(x=1055, y=23)
        CTkLabel(self, text="Sound", text_color="#63C132", fg_color="transparent", 
                font=("Inter", 30), anchor="w", width=112, height=34).place(x=1119, y=23)

        # Indices label
        CTkLabel(self, text="Índices", text_color="#FFFFFF", fg_color="transparent", 
                font=("Inter", 32), width=115, height=38).place(x=245, y=31)

        # Project info labels
        self.lbl_project = CTkLabel(self, text=f"Proyecto: {os.path.basename(self.SELECTED_FOLDER)}", 
                                  text_color="#FFFFFF", fg_color="transparent", 
                                  font=("Inter", 32), anchor="w", width=638, height=38)
        self.lbl_project.place(x=561, y=116)

        self.lbl_location = CTkLabel(self, text=f"Ubicación: {self.SELECTED_FOLDER}", 
                                   text_color="#FFFFFF", fg_color="transparent", 
                                   font=("Inter", 24), anchor="w", width=638, height=38)
        self.lbl_location.place(x=561, y=187)

        self.lbl_progress = CTkLabel(self, text="Archivos Analizados:", 
                                   text_color="#FFFFFF", fg_color="transparent", 
                                   font=("Inter", 32), anchor="w", width=638, height=154)
        self.lbl_progress.place(x=554, y=283)

    def _create_progress_bar(self):
        self.progressbar = CTkProgressBar(self, fg_color="#ACBAB6", 
                                        progress_color="#63C132", width=582, height=14)
        self.progressbar.place(x=553, y=252)
        self.progressbar.set(0)

    def _create_checkboxes(self):
        self.checkbox_list = []
        
        # Select All checkbox
        self.select_all_checkbox = CTkCheckBox(self, text="Seleccionar Todos", 
                                             font=("Inter", 20), text_color="#FFFFFF", 
                                             border_color="#9EE37D", fg_color="#9EE37D", 
                                             hover_color="#9EE37D", bg_color="#272B2B", 
                                             checkmark_color="#272B2B", 
                                             command=self.toggle_all_checkboxes)
        self.select_all_checkbox.place(x=67, y=75)

        # Scrollable panel with indices
        panel_scroll = CTkScrollableFrame(self, width=470, height=500, 
                                        fg_color="#272B2B", border_color="#272B2B", 
                                        border_width=0)
        panel_scroll.place(x=50, y=100)

        for i, index in enumerate(INDICES):
            container = CTkFrame(panel_scroll, fg_color="#9EE37D", 
                               width=451, height=49, corner_radius=7)
            container.pack(pady=5)

            CTkLabel(container, text=index, font=("Inter", 20), 
                    text_color="#525656", anchor="w", width=400, 
                    height=45, fg_color="transparent").place(x=10, y=0)

            checkbox = CTkCheckBox(container, text=None, border_color="#525656",
                                 fg_color="#525656", hover_color="#525656",
                                 bg_color="#9EE37D", checkmark_color="#9EE37D",
                                 corner_radius=15, width=30, height=28)
            checkbox.place(x=410, y=10)

            self.checkbox_list.append((checkbox, i))

    def toggle_all_checkboxes(self):
        for cb, _ in self.checkbox_list:
            cb.select() if self.select_all_checkbox.get() == 1 else cb.deselect()

    def run_indices(self):
        global STOP
        STOP = False

        path_base = self.SELECTED_FOLDER
        total_files = self.count_items(path_base)
        self.lbl_progress.configure(text=f"Archivos Analizados: 0 de {total_files}")

        def analysis_thread():
            if self.last_file:
                indices = self.last_file['indices'] 
            else:
                indices = []
                for cb, i in self.checkbox_list:
                    if cb.get() == 1:
                        indices.append(INDICES[i])
                    
            analizer = Analizer('../config/config.yaml')
            csv_path = "IndicesBioacusticos.csv"
            analizer.set_headers(indices, csv_path)
            analize(path_base, analizer, indices, csv_path, self.last_file,
                   stop_flag=lambda: STOP,
                   update_callback=lambda current: self.update_progress(current, total_files))
            
            self.show_popup("¡El análisis ha terminado!")

        threading.Thread(target=analysis_thread, daemon=True).start()

    def update_progress(self, current, total):
        if hasattr(self, 'lbl_progress') and hasattr(self, 'progressbar'):
            self.lbl_progress.configure(text=f"Archivos Analizados: {current} de {total}")
            self.progressbar.set(current / total if total > 0 else 0)

    def show_popup(self, message):
        popup = CTkToplevel(self)
        popup.title("¡Análisis Completo!")
        popup.configure(fg_color="#272B2B")
        popup_width = 300
        popup_height = 200
        x = (self.winfo_screenwidth() // 2) - (popup_width // 2)
        y = (self.winfo_screenheight() // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        CTkLabel(popup, text=message, text_color="#FFFFFF", 
                font=("Inter", 20), anchor="center").place(relx=0.5, rely=0.4, anchor="center")

        CTkButton(popup, text="Cerrar", font=("Inter", 16), 
                 command=popup.destroy).place(relx=0.5, rely=0.6, anchor="center")

        popup.focus_set()
        popup.grab_set()

    def stop_analysis(self):
        global STOP
        STOP = True
        print("Análisis detenido por el usuario")

    def count_items(self, path_base):
        count = 0
        for root, dirs, files in walk(path_base):
            for file in files:
                if file.lower().endswith('.wav') or file.lower().endswith('.flac'):
                    count += 1
        return count

    def on_back(self):
        print("Back button pressed")

    def on_close(self):
        global STOP
        STOP = True
        self.destroy()

def on_folder_selected(folder_path):
    global app, welcome_app
    if welcome_app:
        welcome_app.destroy()
    app = MainApplication(folder_path)
    if app.last_file:
        app.run_indices()
    app.mainloop()
    

if __name__ == "__main__":
    welcome_app = PipeSoundWelcome(callback=on_folder_selected)
    welcome_app.mainloop()