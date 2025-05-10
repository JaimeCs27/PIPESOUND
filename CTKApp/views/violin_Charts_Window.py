from customtkinter import *
from tkinter import filedialog
from os import path
from PIL import Image
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from controllers.CSV import CSV


class ViolinChartWindow(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self._load_images()
        self.setup_labels()
        self.setup_btn()
        self.csv = None

    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
            if self.img_arrow:
                print("Imágenes cargadas correctamente")
            else:
                print("Alguna imagen no se cargó correctamente.")
        except Exception as e:
            print(f"Error loading images: {e}")
            self.img_arrow = None

    def setup_labels(self):
        # Logo PipeSound (igual que en tu ventana principal)
        self.label_pipe = CTkLabel(self, text="Pipe", text_color="#FFFFFF", 
                                 fg_color="transparent", font=("Inter", 30), 
                                 anchor="w", width=67, height=34)
        self.label_pipe.place(x=1055, y=23)
        
        self.label_sound = CTkLabel(self, text="Sound", text_color="#63C132", 
                                  fg_color="transparent", font=("Inter", 30), 
                                  anchor="w", width=112, height=34)
        self.label_sound.place(x=1119, y=23)
        self.file_label = CTkLabel(self, text="Archivo",fg_color="transparent",
                                    font=("Inter", 15), text_color="#FFFFFF" )
        self.file_label.place(relx=0.25, rely=0.15, anchor="w")

    def setup_btn(self):
        self.select_folder_btn = CTkButton(self, text="Seleccionar Archivo",font=("Inter", 18), fg_color="#63C132", 
                                   hover_color="#63C132", width=200, height=50,
                                   command=self.select_file)
        self.select_folder_btn.place(relx=0.05, rely=0.15, anchor="w")
        self.btn_back = CTkButton(self, text="", fg_color="transparent", 
                                hover_color="#272B2B", command=self.on_back,
                                width=33, height=33, image=self.img_arrow)
        self.btn_back.place(x=51, y=19)

    def select_file(self):
        file = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if file == "":
            print("No se seleccionó ningún archivo")
            return
        self.file_label.configure(text=file)
        self.create_csv(file)

    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")

    def create_csv(self, file):
        self.csv = CSV(file)
        print(self.csv.indices_in_file())
