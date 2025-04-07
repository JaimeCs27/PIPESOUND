from Analizer import Analizer
from acoustic_index import *
from scipy import signal
from os import walk, path
from datetime import datetime
import os
from progress import load_last_processed_file, save_last_processed_file, reset_progress, PROGRESS_FILE


def test():
    analizer = Analizer('config/config.yaml')
    csv_path = "prueba.csv"
    indices = ['Acoustic_Complexity_Index', 'Bio_acoustic_Index', 'Acoustic_Diversity_Index',
               'Acoustic_Evenness_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy',
               'NB_peaks', 'Temporal_Entropy']
    analizer.set_headers(indices, csv_path)

    last_file = load_last_processed_file()

    if last_file:
        choice = input(f"El programa fue interrumpido repentinamente, se encontró progreso previo en '{last_file}'. ¿Desea continuar desde allí? (s/n): ")
        if choice.lower() != 's':
            reset_progress()
            last_file = None

    analize('Test_audios', analizer, indices, csv_path, last_file)

def analize(base_dir, analizer, indices, csv_path, resume_from=None):
    resume = resume_from is not None
    should_skip = True

    all_wavs = []

    for root, _, files in walk(base_dir):
        for filename in sorted(files):
            if filename.endswith('.wav'):
                full_path = path.join(root, filename)
                rel_path = path.relpath(full_path, base_dir)
                all_wavs.append((full_path, rel_path))

    for full_path, rel_path in all_wavs:
        if resume:
            if should_skip:
                if rel_path == resume_from:
                    should_skip = False
                    continue 
                else:
                    continue

        file = AudioFile(full_path, True)

        try:
            analizer.process_audio_file(file, indices)
            analizer.write_to_csv(file, "project a", path.basename(path.dirname(full_path)), csv_path)
            save_last_processed_file(rel_path)
        except Exception as e:
            print(f"Error procesando {rel_path}: {e}")
            return

    if path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)



test()
