import json
from acoustic_index import *
from scipy import signal
from os import walk, path, remove
from datetime import datetime
import os
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from Analizer import *

class Process(mp.Process):
    def __init__(self, id, full_path, rel_path):
        super(Process, self).__init__()
        self.full_path = full_path
        self.rel_path = rel_path
        self.id = id
        
    
    def run(self):
        try:
            file = AudioFile(self.full_path, True)
            analizer.process_audio_file(file, indices)
            print(f"Proceso {self.id} completado para {self.full_path}")
            #analizer.write_to_csv(file, "project a", path.basename(path.dirname(self.full_path)), csv_path)
            #processed_count += 1
            #save_last_processed_data(base_dir, self.full_path, indices)
        except Exception as e:
            print(f"Error procesando {self.full_path}: {e}")

def create_temp_audio_file():
    """No hace nada, solo es un placeholder."""
    pass


def test():
    """Function to test parallelism with analize() function."""
    analizer = Analizer('../config/config.yaml')
    print(analizer)
    #resume = resume_from is not None
    should_skip = True

    all_wavs = []
    flac_files = []

    base_dir = 'C:/Users/sebas/Desktop/Archivos audio'

    # # Recopilar rutas de archivos .wav y .flac

    print("Buscando archivos en ", base_dir)
    for root, _, files in walk(base_dir):
        for filename in sorted(files):
            full_path = path.join(root, filename)
            if filename.endswith('.wav'):
                rel_path = path.relpath(full_path, base_dir)
                all_wavs.append((full_path, rel_path))
            elif filename.endswith('.flac'):
                flac_files.append(full_path)

    print(f"Archivos encontrados para procesar: {len(all_wavs)}")

    # # Convertir archivos .flac a .wav en paralelo
    # with ThreadPoolExecutor() as executor:
    #     executor.map(convert_to_wav, flac_files)

    # # Agregar archivos .wav nuevos generados por la conversión
    # for flac_path in flac_files:
    #     wav_path = os.path.splitext(flac_path)[0] + '.wav'
    #     if path.exists(wav_path):
    #         rel_path = path.relpath(wav_path, base_dir)
    #         all_wavs.append((wav_path, rel_path))

    processed_count = 0
    total_files = len(all_wavs)
    print(f"Total de archivos a procesar: {total_files}")


    # Este codigo es paralelo
    


    #Este codigo es serial
    # for full_path, rel_path in all_wavs:
    #     if resume:
    #         if should_skip:
    #             if full_path == resume_from['file']:  # Ahora comparamos con full_path
    #                 processed_count+=1
    #                 should_skip = False
    #                 continue 
    #             else:
    #                 processed_count+=1
    #                 continue

    #     file = AudioFile(full_path, True)

    #     try:
    #         if stop_flag and stop_flag():
    #             print("Análisis detenido por el usuario.")
    #             archivos = ["prueba.csv", PROGRESS_FILE]
    #             for archivo in archivos:
    #                 if path.exists(archivo):
    #                     remove(archivo)
    #             return

    #         analizer.process_audio_file(file, indices)
    #         analizer.write_to_csv(file, "project a", path.basename(path.dirname(full_path)), csv_path)
    #         processed_count += 1
    #         save_last_processed_data(base_dir, full_path, indices)

    #         if update_callback:
    #             update_callback(processed_count, total_files)

    #     except Exception as e:
    #         print(f"Error procesando {full_path}: {e}")
    #         return

    # reset_progress()

if __name__ == "__main__":
    test()