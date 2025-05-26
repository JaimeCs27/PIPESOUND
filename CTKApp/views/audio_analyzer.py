from customtkinter import *
from PIL import Image
import sys
from os import path, walk, listdir
import os
import threading
import time
import multiprocessing as mp
# Agrega la carpeta superior al path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from controllers.analizer import *
from controllers.progress import load_last_processed_data, reset_progress, PROGRESS_PATH, analize

# Global variables
STOP = False
SELECTED_FOLDER = None
app = None  
welcome_app = None
INDICES = ['Acoustic_Complexity_Index', 'Acoustic_Diversity_Index',
               'Acoustic_Evenness_Index', 'Bio_acoustic_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy',
               'NB_peaks', 'Temporal_Entropy', 'Wave_Signal_To_Noise_Ratio']

INDEX_COLORS = {
    "Acoustic_Complexity_Index": "#9EE37D",
    "Acoustic_Diversity_Index": "#9EE37D",
    "Acoustic_Evenness_Index": "#9EE37D",
    "Bio_acoustic_Index": "#9EE37D",
    "Normalized_Difference_Sound_Index": "#87B38D",
    "Wave_Signal_To_Noise_Ratio": "#87B38D",
    "Spectral_Entropy": "#E2E8CE",
    "Temporal_Entropy": "#E2E8CE",
    "NB_peaks": "#D0FFD6",
}



class AudioAnalyzer(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SELECTED_FOLDER = ""
        self.configure(fg_color="#272B2B")  
        self.bg_color = "#272B2B"
        self._create_widgets()
        self.last_file = load_last_processed_data()
        self.stop_event = mp.Event()

    def receive_data(self, **kwargs):
        folder = kwargs.get("folder_path", "")
        if folder:
            self.SELECTED_FOLDER = folder
            self._refresh_labels()
            resume = kwargs.get("resume", False)
            if resume and self.last_file:
                self.run_indices()
                

    def _refresh_labels(self):
        base = os.path.basename(self.SELECTED_FOLDER) or "No selected folder"
        self.lbl_project.configure(text=f"Project: {base}")
        self.lbl_location.configure(text=f"Location: {self.SELECTED_FOLDER or '—'}")


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
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
            self.img_run = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Run.png")))
            self.img_stop = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Stop.png")))
            if self.img_arrow and self.img_run and self.img_stop:
                print("Images loaded successfully")
            else:
                print("Some images failed to load.")
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
        self.btn_run = CTkButton(self, text="Run", font=("Inter", 36), 
                               fg_color="#63C132", hover_color="#63C132", 
                               command=self.run_indices, width=448, height=49, image=self.img_run)
        self.btn_run.place(x=79, y=627)

        # Stop button
        self.btn_stop = CTkButton(self, text="Stop", font=("Inter", 36), 
                                fg_color="#F21D1D", hover_color="#F21D1D", 
                                command=self.stop_analysis, width=448, height=49, image=self.img_stop)
        self.btn_stop.place(x=659, y=627)

    def _create_labels(self):
        # PipeSound label
        CTkLabel(self, text="Pipe", text_color="#FFFFFF", fg_color="transparent", 
                font=("Inter", 30), anchor="w", width=67, height=34).place(x=1055, y=23)
        CTkLabel(self, text="Sound", text_color="#63C132", fg_color="transparent", 
                font=("Inter", 30), anchor="w", width=112, height=34).place(x=1119, y=23)

        # Indices label
        CTkLabel(self, text="Indixes", text_color="#FFFFFF", fg_color="transparent", 
                font=("Inter", 32), width=115, height=38).place(x=245, y=31)

        # Project info labels
        self.lbl_project = CTkLabel(self, text=f"Project: {os.path.basename(self.SELECTED_FOLDER)}", 
                                  text_color="#FFFFFF", fg_color="transparent", 
                                  font=("Inter", 32), anchor="w", width=638, height=38)
        self.lbl_project.place(x=561, y=116)

        self.lbl_location = CTkLabel(self, text=f"Location: {self.SELECTED_FOLDER}", 
                                   text_color="#FFFFFF", fg_color="transparent", 
                                   font=("Inter", 24), anchor="w", width=638, height=38)
        self.lbl_location.place(x=561, y=187)

        self.lbl_progress = CTkLabel(self, text="Processed Files:", 
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
        self.select_all_checkbox = CTkCheckBox(self, text="Select All", 
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
            color = INDEX_COLORS.get(index, "#9EE37D")  # Default a verde si no se encuentra

            container = CTkFrame(panel_scroll, fg_color=color, 
                                width=451, height=49, corner_radius=7)
            container.pack(pady=5)

            CTkLabel(container, text=index.replace("_", " "), font=("Inter", 20), 
                    text_color="#272B2B", anchor="w", width=400, 
                    height=45, fg_color="transparent").place(x=10, y=0)

            checkbox = CTkCheckBox(container, text=None, border_color="#272B2B",
                                fg_color="#272B2B", hover_color="#272B2B",
                                bg_color=color, checkmark_color=color,
                                corner_radius=15, width=30, height=28)
            checkbox.place(x=410, y=10)

            self.checkbox_list.append((checkbox, i))


    def toggle_all_checkboxes(self):
        for cb, _ in self.checkbox_list:
            cb.select() if self.select_all_checkbox.get() == 1 else cb.deselect()

    def run_indices(self):
        global STOP
        STOP = False
        self.stop_event.clear()
        path_base = self.SELECTED_FOLDER
        total_files = self.count_items(path_base)
        self.lbl_progress.configure(text=f"Processed Files: 0 out of {total_files}")

        

        def analysis_thread():
            if self.last_file:
                indices = self.last_file['indices'] 
            else:
                indices = []
                for cb, i in self.checkbox_list:
                    if cb.get() == 1:
                        indices.append(INDICES[i])
            config_path = path.join(path.dirname(__file__), "../config/config.yaml")
            analizer = Analizer(config_path)
            csv_path = path.join(path.dirname(__file__), "IndicesBioacusticos.csv")
            if (path.exists(csv_path)):
                os.remove(csv_path)
            temp_path = path.join(path.dirname(__file__), "temp_audio_files")
            analizer.set_headers(indices, csv_path)
            analize(path_base, analizer, indices, csv_path, temp_path, self.last_file,
                   stop_event = self.stop_event,
                   update_callback=lambda current, total: self.update_progress(current, total_files))
            self.show_popup("¡The analysis has finished!")

        threading.Thread(target=analysis_thread, daemon=True).start()

    def update_progress(self, current, total):
        if hasattr(self, 'lbl_progress') and hasattr(self, 'progressbar'):
            self.lbl_progress.configure(text=f"Processed Files: {current} out of {total}")
            self.progressbar.set(current / total if total > 0 else 0)

    def show_popup(self, message):
        popup = CTkToplevel(self)
        popup.title("¡Analysis Completed!")
        popup.configure(fg_color="#272B2B")
        popup_width = 300
        popup_height = 200
        x = (self.winfo_screenwidth() // 2) - (popup_width // 2)
        y = (self.winfo_screenheight() // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        CTkLabel(popup, text=message, text_color="#FFFFFF", 
                font=("Inter", 20), anchor="center").place(relx=0.5, rely=0.4, anchor="center")

        CTkButton(popup, text="Close", font=("Inter", 16), 
                 command=popup.destroy).place(relx=0.5, rely=0.6, anchor="center")

        popup.focus_set()
        popup.grab_set()

    def stop_analysis(self):
        global STOP
        STOP = True
        self.stop_event.set()
        print("Analysis stopped by user")

    def count_items(self, path_base):
        count = 0
        supported_extensions = ('.wav', '.flac', '.mp3')
        for root, dirs, files in walk(path_base):
            for file in files:
                if file.lower().endswith(supported_extensions):
                    count += 1
        return count

    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")