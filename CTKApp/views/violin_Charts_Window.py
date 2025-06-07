from customtkinter import *
from tkinter import filedialog
from os import path
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
from controllers.CSV import CSV



class ViolinChartWindow(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(fg_color="#272B2B")

        self.controller = controller
        self._load_images()
        self.setup_labels()
        self.setup_btn()
        self.csv = None
        self.index_buttons = []
        self.index_columns = []
        self.display_to_real_index = {}
        self.index_menu = None
        self.plot_btn = None


    def _load_images(self):
        try:
            self.img_arrow = CTkImage(Image.open(path.join(path.dirname(__file__), "icons\Arrow.png")))
        except Exception as e:
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
            print("No file selected.")
            return
        self.file_label.configure(text=file)
        self.create_csv(file)


    def on_back(self):
        self.controller.show_frame("PipeSoundWelcome")

    
    def create_csv(self, file):
        self.csv = CSV(file)
        df = self.csv.to_dataframe()

        self.index_columns = [col for col in df.columns if col not in ['project_name', 'site', 'date', 'time', 'filename']]
        if not self.index_columns:
            print("No valid indices found.")
            return

        # Crear diccionario: nombre con espacios → nombre real
        self.display_to_real_index = {col.replace("_", " "): col for col in self.index_columns}
        display_names = list(self.display_to_real_index.keys())

        # Crear o actualizar dropdown
        if self.index_menu is None:
            self.index_menu = CTkOptionMenu(
                self,
                values=display_names,
                width=200,
                height=40,
                font=("Inter", 15),
                fg_color="#272B2B",
                button_color="#272B2B",
                button_hover_color="#ACBAB6",
                text_color="#FFFFFF"
            )
            self.index_menu.place(relx=0.05, rely=0.25, anchor="w")
        else:
            self.index_menu.configure(values=display_names)
        self.index_menu.set(display_names[0]) 

        if self.plot_btn is None:
            self.plot_btn = CTkButton(
                self, text="Graficar índice", font=("Inter", 18),
                fg_color="#63C132", hover_color="#63C132",
                width=200, height=50, command=self.plot_violin_chart
            )
            self.plot_btn.place(relx=0.05, rely=0.35, anchor="w")
        else:
            self.plot_btn.configure(state="normal")


    def plot_violin_chart(self):
        if self.csv is None or self.index_menu is None:
            print("No CSV loaded or menu not available.")
            return

        selected_display = self.index_menu.get()
        real_index = self.display_to_real_index.get(selected_display)

        if real_index is None:
            print(f"Index '{selected_display}' not found in the mapping.")
            return

        df = self.csv.to_dataframe()

        plt.figure(figsize=(10, 6))
        sns.violinplot(x="site", y=real_index, data=df, inner="box", palette="Set2")
        plt.title(f"Distribución del índice '{selected_display}' por site")
        plt.xlabel("Site")
        plt.ylabel(selected_display)
        plt.tight_layout()
        plt.show()


