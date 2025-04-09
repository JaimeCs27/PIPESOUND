from customtkinter import *
from PIL import Image
import sys
import os
import threading
# Agrega la carpeta superior al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Analizer import *
from progress import load_last_processed_file, save_last_processed_file, reset_progress, PROGRESS_FILE, analize

STOP = False

app = CTk()
app.geometry("1280x720")
#Fondo del app
app.configure(fg_color="#272B2B")

#Boton Retroceder
img = Image.open("icons/Arrow.png")
btn = CTkButton(app, text="", fg_color="transparent", hover_color="#272B2B", command=lambda: print("Botón presionado"), width=33, height=33, image=CTkImage(img))
btn.place(x=51, y=19)

#Boton Confirmar
img2 = Image.open("icons/Run.png")
btn2 = CTkButton(app, text="Correr", font=("Inter", 36), fg_color="#63C132", hover_color="#63C132", command=lambda: run_indices(), width=448, height=49, image=CTkImage(img2))
btn2.place(x=79, y=627)

#Boton Cancelar
img3 = Image.open("icons/Stop.png")
btn3 = CTkButton(app, text="Detener", font=("Inter", 36), fg_color="#F21D1D", hover_color="#F21D1D", command=lambda: stop(), width=448, height=49, image=CTkImage(img3))
btn3.place(x=659, y=627)

#Label PipeSound
label = CTkLabel(app, text="Pipe", text_color="#FFFFFF", fg_color="transparent", font=("Inter", 30), anchor="w", width=67, height=34)
label.place(x=1055, y=23)
label2 = CTkLabel(app, text="Sound", text_color="#63C132", fg_color="transparent", font=("Inter", 30), anchor="w", width=112, height=34)
label2.place(x=1119, y=23)

#Label Indices
label3 = CTkLabel(app, text="Índices", text_color="#FFFFFF", fg_color="transparent", font=("Inter", 32), width=115, height=38)
label3.place(x=245, y=31)

#Label Proyecto
label4 = CTkLabel(app, text="Proyecto: Mi Proyecto", text_color="#FFFFFF", fg_color="transparent", font=("Inter", 32), anchor="w", width=638, height=38)
label4.place(x=561, y=116)

#Label Site
label5 = CTkLabel(app, text="Site: Mi Site", text_color="#FFFFFF", fg_color="transparent", font=("Inter", 32), anchor="w", width=638, height=38)
label5.place(x=561, y=187)

#Label Archivos
label6 = CTkLabel(app, text="Archivos Analizados: 66 de 368", text_color="#FFFFFF", fg_color="transparent", font=("Inter", 32), anchor="w", width=638, height=154)
label6.place(x=554, y=283)

#Slider Progreso
progressbar = CTkProgressBar(app, fg_color="#ACBAB6", progress_color="#63C132", width=582, height=14)
progressbar.place(x=553, y=252)

#ScrollBar
# scrollbar = CTkScrollbar(app, orientation="vertical", fg_color="#D9D9D9", button_color="#272B2B", hover=False, width=8, height=536)
# scrollbar.place(x=530, y=83)

#Prueba Indice
# btn4 = CTkButton(app, text="Acoustic Complexity Index", text_color="#525656", anchor="w", font=("Inter", 26), fg_color="#9EE37D", hover_color="#9EE37D", command=lambda: print("Botón presionado"), width=451, height=49)
# btn4.place(x=70, y=105)
# checkbox = CTkCheckBox(app,
#                        text=None,
#                        textvariable=None,
#                        border_color="#525656",   # Color del borde
#                        fg_color="#525656",       # Color de fondo cuando está marcado
#                        hover_color="#525656",    # Color al hacer hover
#                        bg_color="#9EE37D",       # Fondo detrás del checkbox (el botón verde)
#                        checkmark_color="#9EE37D",# Color del "check" interno
#                        corner_radius=15,         # Hace el checkbox redondo
#                        width=29,
#                        height=29)
# checkbox.place(x=452, y=116)

# Lista para guardar checkboxes individuales
checkbox_list = []

# Checkbox "Seleccionar Todos"
def toggle_all():
    for cb, _ in checkbox_list:
        cb.select() if select_all_checkbox.get() == 1 else cb.deselect()

select_all_checkbox = CTkCheckBox(app,
                                  text="Seleccionar Todos",
                                  font=("Inter", 20),
                                  text_color="#FFFFFF",
                                  border_color="#9EE37D",
                                  fg_color="#9EE37D",
                                  hover_color="#9EE37D",
                                  bg_color="#272B2B",
                                  checkmark_color="#272B2B",
                                  command=toggle_all)
select_all_checkbox.place(x=67, y=75)

# Scrollable panel
panel_scroll = CTkScrollableFrame(app, width=470, height=500, fg_color="#272B2B", border_color="#272B2B", border_width=0)
panel_scroll.place(x=50, y=100)

INDICES = ['Acoustic_Complexity_Index', 'Acoustic_Diversity_Index',
               'Acoustic_Evenness_Index', 'Bio_acoustic_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy',
               'NB_peaks', 'Temporal_Entropy', 'Wave_Signal_To_Noise_Ratio']

# Crear múltiples entradas
for i in range(len(INDICES)):
    container = CTkFrame(panel_scroll, fg_color="#9EE37D", width=451, height=49, corner_radius=7)
    container.pack(pady=5)

    label = CTkLabel(container,
                     text=INDICES[i],
                     font=("Inter", 26),
                     text_color="#525656",
                     anchor="w",
                     width=400,
                     height=45,
                     fg_color="transparent")
    label.place(x=10, y=0)

    checkbox = CTkCheckBox(container,
                           text=None,
                           border_color="#525656",
                           fg_color="#525656",
                           hover_color="#525656",
                           bg_color="#9EE37D",
                           checkmark_color="#9EE37D",
                           corner_radius=15,
                           width=30,
                           height=28)
    checkbox.place(x=410, y=10)

    checkbox_list.append((checkbox, i))  # Guardar referencia a cada checkbox


def run_indices():
    global STOP
    STOP = False

    def analysis_thread():
        indices = []
        for cb, i in checkbox_list:
            if cb.get() == 1:
                indices.append(INDICES[i])
        analizer = Analizer('../config/config.yaml')
        csv_path = "prueba.csv"
        last_file = load_last_processed_file()
        analizer.set_headers(indices, csv_path)
        if last_file:
            choice = input(f"El programa fue interrumpido repentinamente, se encontró progreso previo en '{last_file}'. ¿Desea continuar desde allí? (s/n): ")
            if choice.lower() != 's':
                reset_progress()
                last_file = None

        analize('../Test_audios', analizer, indices, csv_path, last_file, stop_flag=lambda: STOP)

    threading.Thread(target=analysis_thread, daemon=True).start()
   
def stop():
    global STOP
    STOP = True
    

    print("Se ha solicitado detener el análisis.")

app.mainloop()