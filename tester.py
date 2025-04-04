from Analizer import Analizer
from acoustic_index import *
from scipy import signal
from os import walk, path
from datetime import datetime

def test():
    analizer = Analizer('config/config.yaml')
    csv_path = "prueba.csv"
    indices =['Acoustic_Complexity_Index', 'Bio_acoustic_Index', 'Acoustic_Diversity_Index', 'Acoustic_Evenness_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy', 'NB_peaks', 'Temporal_Entropy']
    analizer.set_headers(indices, csv_path)
    analize('Test_audios', analizer, indices, csv_path)

def analize(dir, analizer, indices, csv_path):
    for root, _, files in walk(dir):  # root = directorio actual, files = archivos en root
        for filename in files:
            if filename.endswith('.wav'):
                file_path = path.join(root, filename)  # Usar os.path.join correctamente
                file = AudioFile(file_path, True)
                analizer.process_audio_file(file, indices)
                analizer.write_to_csv(file, "project a", path.basename(root), csv_path)  # Corregir os.path.basename

test()