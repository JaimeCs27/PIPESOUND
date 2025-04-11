import json
from Analizer.acoustic_index import *
from scipy import signal
from os import walk, path, remove
from datetime import datetime

PROGRESS_FILE = 'progress.txt'

def load_last_processed_data():
    """Carga el último archivo procesado y los índices desde PROGRESS_FILE."""
    if path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            try:
                return json.load(f)  # Carga el JSON con file e indices
            except json.JSONDecodeError:
                return None
    return None

def save_last_processed_data(root, file_full_path, indices):
    """Guarda la ruta completa del último archivo procesado y los índices en JSON."""
    data = {
        "root": root,
        "file": file_full_path,
        "indices": indices
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f)

def reset_progress():
    """Elimina el archivo de progreso."""
    if path.exists(PROGRESS_FILE):
        remove(PROGRESS_FILE)

def analize(base_dir, analizer, indices, csv_path, resume_from=None, stop_flag=None, update_callback=None):
    """Analiza los archivos de audio en base_dir y guarda el progreso."""
    resume = resume_from is not None
    should_skip = True

    all_wavs = []

    # Obtener lista de archivos .wav con rutas completas y relativas
    for root, _, files in walk(base_dir):
        for filename in sorted(files):
            if filename.endswith('.wav'):
                full_path = path.join(root, filename)
                rel_path = path.relpath(full_path, base_dir)
                all_wavs.append((full_path, rel_path))

    processed_count = 0

    for full_path, rel_path in all_wavs:
        if resume:
            if should_skip:
                if full_path == resume_from['file']:  # Ahora comparamos con full_path
                    processed_count+=1
                    should_skip = False
                    continue 
                else:
                    processed_count+=1
                    continue

        file = AudioFile(full_path, True)

        try:
            if stop_flag and stop_flag():
                print("Análisis detenido por el usuario.")
                archivos = ["prueba.csv", PROGRESS_FILE]

                for archivo in archivos:
                    if path.exists(archivo):
                        remove(archivo)
                return

            analizer.process_audio_file(file, indices)
            analizer.write_to_csv(file, "project a", path.basename(path.dirname(full_path)), csv_path)
            processed_count += 1
            save_last_processed_data(base_dir, full_path, indices)  # Guarda archivo e índices

            if update_callback:
                update_callback(processed_count)

        except Exception as e:
            print(f"Error procesando {full_path}: {e}")
            return

    reset_progress()  # Elimina PROGRESS_FILE al completar todo
