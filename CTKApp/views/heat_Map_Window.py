from datetime import datetime
from customtkinter import *
from tkinter import filedialog
from os import path
from PIL import Image
import seaborn as sns
import pandas as pd
import librosa
import threading
import matplotlib.pyplot as plt
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from controllers.CSV import CSV
import csv
import numpy as np



class HeatMapWindow(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(fg_color="#272B2B")

        self.controller = controller
        self._load_images()
        self.setup_labels()
        self.setup_btn()
        self.loading_setup()
        self.csv = None
        self.index_buttons = []
        self.index_columns = []
        self.display_to_real_index = {}
        self.index_menu = None
        self.plot_btn = None

    def hide_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.place_forget()  # Oculta la barra completamente

        

    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))

        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None

    def setup_labels(self):
        self.label_pipe = CTkLabel(self, text="Pipe", text_color="#FFFFFF", 
                                 fg_color="transparent", font=("Inter", 30), 
                                 anchor="w", width=67, height=34)
        self.label_pipe.place(x=1055, y=23)
        
        self.label_sound = CTkLabel(self, text="Sound", text_color="#63C132", 
                                  fg_color="transparent", font=("Inter", 30), 
                                  anchor="w", width=112, height=34)
        self.label_sound.place(x=1119, y=23)
        self.file_label = CTkLabel(self, text="File",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF" )
        self.file_label.place(relx=0.25, rely=0.15, anchor="w")

    def loading_setup(self):
        self.progress_bar = CTkProgressBar(self, width=300)
        
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.stop()

    def setup_btn(self):
        self.select_folder_btn = CTkButton(self, text="Choose Folder",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=200, height=50,
                                   command=self.select_folder)
        self.select_folder_btn.place(relx=0.05, rely=0.15, anchor="w")
        self.btn_back = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.btn_back.place(x=51, y=19)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select a folder with audio files")
        if folder == "":
            print("No folder selected")
            return
        self.file_label.configure(text=folder)

        # Procesar la carpeta en un hilo aparte
        threading.Thread(target=self.process_folder, args=(folder,), daemon=True).start()


    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")

    def get_sample_rate(self, file_path):
        try:
            y, sr = librosa.load(file_path, sr=None)
            pitches = librosa.yin(y, fmin=50, fmax=2000, sr=sr)

            pitches = pitches[~np.isnan(pitches)]

            if len(pitches) == 0:
                return None

            dominant = np.median(pitches)
            return round(dominant, 2) 
        except Exception as e:
            print(f"It was not possible to calculate the dominant frequency of {file_path}: {e}")
            return None

    def extract_time_from_filename(self, filename):
        try:
            parts = filename.split("_")
            if len(parts) >= 3:
                raw_time = parts[-1].replace(".wav", "").replace(".mp3", "").replace(".flac", "")
                formatted_time = raw_time.replace("-", ":")  
                return formatted_time
            else:
                return "N/A"
        except Exception as e:
            print(f"Could not extract time from {filename}: {e}")
            return "N/A"

    def process_folder(self, folder):
        audio_extensions = (".flac", ".wav", ".mp3")
        data = []
        self.progress_bar.place(relx=0.05, rely=0.3, anchor="w")
        self.progress_bar.start()
        self.progress_bar.update()
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(audio_extensions):
                    file_path = os.path.join(root, file)
                    sample_rate = self.get_sample_rate(file_path)
                    file_date = self.extract_time_from_filename(file_path)
                    if sample_rate is not None:
                        deepest_folder = os.path.basename(root)
                        data.append([deepest_folder, file, sample_rate, file_date])
                    else:
                        print(f"Skipping {file} due to error.")

        if not data:
            print("No valid audio files found.")
            return

        output_csv = os.path.join(folder, "audio_metadata.csv")
        with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["folder", "filename", "sample_rate", "date"])
            writer.writerows(data)

        print(f"CSV created at: {output_csv}")
        self.hide_progress_bar()
        self.generar_heatmaps(output_csv)
        


    def generar_heatmaps(self, csv_path):
        df = pd.read_csv(csv_path)

        df['freq_int'] = df['sample_rate'].round().astype(int)
        df['hour'] = pd.to_datetime(df['date'], format='%H:%M:%S').dt.hour

        output_dir = os.path.join(os.path.dirname(csv_path), "heatmaps")
        os.makedirs(output_dir, exist_ok=True)

        for folder in df['folder'].unique():
            sub_df = df[df['folder'] == folder]
            heatmap_data = sub_df.pivot_table(
                index='freq_int',
                columns='hour',
                values='filename',
                aggfunc='count',
                fill_value=0
            )
            heatmap_percent = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100

            plt.figure(figsize=(12, 6))
            ax = sns.heatmap(
                heatmap_percent,
                cmap="hot",
                cbar_kws={'label': '% of frecuencies in files'},
                vmin=0, vmax=100
            )

            plt.title(f"Heatmap of frequencies for folder: {folder}")
            plt.xlabel("Hour of the day")
            plt.ylabel("Frequency (Hz)")
            plt.xticks(rotation=0)

            # Configurar ticks del eje Y de 10 en 10
            freq_ticks = range(int(heatmap_percent.index.min()), int(heatmap_percent.index.max()) + 1, 10)
            ax.set_yticks(freq_ticks)
            ax.set_yticklabels(freq_ticks, rotation=0)

            # Invertir eje Y (para que frecuencias bajas estén más cerca del eje X)
            ax.invert_yaxis()

            plt.tight_layout()
            plt.savefig(f"{output_dir}/{folder}_heatmap.png")
            plt.show()
            plt.close()


                