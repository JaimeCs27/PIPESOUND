from Analizer import Analizer
from acoustic_index import *
from scipy import signal
from os import walk, path
from datetime import datetime
import os
from progress import load_last_processed_file, save_last_processed_file, reset_progress, PROGRESS_FILE, analize


def test():
    analizer = Analizer('config/config.yaml')
    csv_path = "prueba.csv"
    indices = ['Acoustic_Complexity_Index', 'Bio_acoustic_Index', 'Acoustic_Diversity_Index',
               'Acoustic_Evenness_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy',
               'NB_peaks', 'Temporal_Entropy', 'Wave_Signal_To_Noise_Ratio']
    analizer.set_headers(indices, csv_path)

    last_file = load_last_processed_file()

    if last_file:
        choice = input(f"El programa fue interrumpido repentinamente, se encontró progreso previo en '{last_file}'. ¿Desea continuar desde allí? (s/n): ")
        if choice.lower() != 's':
            reset_progress()
            last_file = None

    analize('Test_audios', analizer, indices, csv_path, last_file)
    




test()
