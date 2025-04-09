from os import path
import os
from acoustic_index import *
from scipy import signal
from os import walk, path
from datetime import datetime
import Analizer

PROGRESS_FILE = 'progress.txt'

def load_last_processed_file():
    if path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_processed_file(file_rel_path):
    with open(PROGRESS_FILE, 'w') as f:
        f.write(file_rel_path)

def reset_progress():
    if path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

def analize(base_dir, analizer, indices, csv_path, resume_from=None, stop_flag=None):
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
            if stop_flag and stop_flag():
                print("Análisis detenido por el usuario.")
                return
            analizer.process_audio_file(file, indices)
            analizer.write_to_csv(file, "project a", path.basename(path.dirname(full_path)), csv_path)
            save_last_processed_file(rel_path)
        except Exception as e:
            print(f"Error procesando {rel_path}: {e}")
            return

    if path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)