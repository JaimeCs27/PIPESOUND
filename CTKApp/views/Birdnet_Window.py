from customtkinter import *
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from PIL import Image
import sys
from os import path
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
import csv


class BirdnetWindow(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._load_images()
        self.label_setup()
        self.btn_setup()
        self.entries_setup()
        self.file = ""
        self.labels = []
        self.results = []

    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None

    def entries_setup(self):
        self.lat_txt = CTkEntry(self, width=100,font=("Inter", 15))
        self.lat_txt.place(relx=0.05, rely=0.35, anchor="w")
        self.lon_txt = CTkEntry(self, width=100,font=("Inter", 15))
        self.lon_txt.place(relx=0.15, rely=0.35, anchor="w")

    def label_setup(self):
        self.label_pipe = CTkLabel(self, text="Pipe", text_color="#FFFFFF", 
                                 fg_color="transparent", font=("Inter", 30), 
                                 anchor="w", width=67, height=34)
        self.label_pipe.place(x=1055, y=23)

        self.label_sound = CTkLabel(self, text="Sound", text_color="#63C132", 
                                  fg_color="transparent", font=("Inter", 30), 
                                  anchor="w", width=112, height=34)
        self.label_sound.place(x=1119, y=23)
        self.file_label = CTkLabel(self, text="Folder Location",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF")
        self.file_label.place(relx=0.25, rely=0.2, anchor="w")
        self.lat_label = CTkLabel(self, text="Latitude",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF")
        self.lat_label.place(relx=0.05, rely=0.3, anchor="w")
        self.lon_label = CTkLabel(self, text="Longitude",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF")
        self.lon_label.place(relx=0.15, rely=0.3, anchor="w")
        self.result_label = CTkLabel(self, text="",fg_color="transparent",
                                    font=("Inter", 30), text_color="#FFFFFF")
        self.result_label.place(relx=0.05, rely=0.43, anchor="w")
        self.birds = CTkScrollableFrame(self, width=700, height=300, fg_color="#131616")
        self.birds.place(relx=0.05, rely=0.46, anchor='nw')

        


    def btn_setup(self):
        self.btn_file = CTkButton(self, text="Select File",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=200, height=45,
                                   command=self.select_file)
        self.btn_file.place(relx=0.05, rely=0.2, anchor="w")
        self.analyze_btn = CTkButton(self, text="Analyze",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=100, height=35,
                                   command=self.analyze)
        self.analyze_btn.place(relx= 0.25, rely=0.35, anchor="w")
        self.back_btn = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.back_btn.place(relx=0.02, rely=0.05, anchor="w")
        self.save_csv = CTkButton(self, text="Save Result",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=100, height=35,
                                   command=self.create_csv)
        self.save_csv.place(relx= 0.35, rely=0.35, anchor="w")

    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")

    def select_file(self):
        self.file = filedialog.askopenfile(filetypes=[("WAV Files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*")],
                                            title="Select an audio file")
        self.file_label.configure(text=self.file.name)

    def create_csv(self):
        if len(self.result) <= 0:
            print("Not result given")
            return
        output_file = "Birdnet_result.csv"
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.result[0].keys())
            writer.writeheader()
            writer.writerows(self.result)

        print(f"File save in {output_file}")

    def clean(self):
        for label in self.labels:
            label.destroy()
        self.birds.update()  # Forzar refresco
        self.labels.clear()

    def analyze(self):
        if (self.file == ""):
            print("Not file selected")
            return
        lat = ""
        lon = ""
        analyzer = Analyzer()
        try:
            lat = self.lat_txt.get()
            if (lat != ""):
                lat = float(lat)
        except ValueError:
            print("Wrong latitud value given, has to be empty or a float")
        try:
            lon = self.lon_txt.get()
            if (lon != ""):
                lon = float(lon)
        except ValueError:
            print("Wrong longitud value given, has to be empty or a float")

        self.clean()
        recording = None
        if lat == "" and lon == "":
            recording = Recording(analyzer, self.file.name, min_conf=0.25)
        else:
            recording = Recording(analyzer,self.file.name, lat=lat, lon=lon, min_conf=0.2)
        if recording is None:
            print("Error while analyzing")
            return
        recording.analyze()
        self.result = recording.detections
        result = self.result
        if result == []:
            self.result_label.configure(text="No matches found")
            return
        else:
            self.result_label.configure(text="Results")
            for element in result:
                name_label = CTkLabel(self.birds, text="Known as: "+str(element["common_name"]),fg_color="transparent",
                                            font=("Inter", 20), text_color="#FFFFFF")
                name_label.pack(anchor="w", pady=1, padx=1)
                scientific_name = CTkLabel(self.birds, text="Scientific name: "+str(element["scientific_name"]),fg_color="transparent",
                                            font=("Inter", 15), text_color="#FFFFFF")
                scientific_name.pack(anchor="w", pady=1, padx=1)
                confidence = CTkLabel(self.birds, text="Confidence Level: "+str(element["confidence"]),fg_color="transparent",
                                            font=("Inter", 15), text_color="#FFFFFF")
                confidence.pack(anchor="w", pady=1, padx=1)
                seconds = CTkLabel(self.birds, text="Between seconds "+ str(element["start_time"]) + " - " + str(element["end_time"]),fg_color="transparent",
                                            font=("Inter", 15), text_color="#FFFFFF")
                seconds.pack(anchor="w", pady=1, padx=1)
                self.labels.append(name_label)
                self.labels.append(scientific_name)
                self.labels.append(confidence)
                self.labels.append(seconds)
        

        

