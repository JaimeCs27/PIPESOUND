import json
from Analizer.acoustic_index import *
from scipy import signal
from os import walk, path, remove
from datetime import datetime
import os
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor

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

def convert_to_wav(file_path):
    if file_path.lower().endswith('.flac'):
        try:
            data, samplerate = sf.read(file_path)
            wav_path = os.path.splitext(file_path)[0] + '.wav'
            sf.write(wav_path, data, samplerate)
            print(f'Archivo convertido y guardado como: {wav_path}')

            os.remove(file_path)
            print(f'Archivo .flac eliminado: {file_path}')

        except Exception as e:
            print(f"Error al convertir {file_path}: {e}")

def analize(base_dir, analizer, indices, csv_path, resume_from=None, stop_flag=None, update_callback=None):
    """Analiza los archivos de audio en base_dir y guarda el progreso."""
    resume = resume_from is not None
    should_skip = True

    all_wavs = []
    flac_files = []

    # Recopilar rutas de archivos .wav y .flac
    for root, _, files in walk(base_dir):
        for filename in sorted(files):
            full_path = path.join(root, filename)
            if filename.endswith('.wav'):
                rel_path = path.relpath(full_path, base_dir)
                all_wavs.append((full_path, rel_path))
            elif filename.endswith('.flac'):
                flac_files.append(full_path)

    with ThreadPoolExecutor() as executor:
        executor.map(convert_to_wav, flac_files)

    # Agregar archivos .wav nuevos generados por la conversión
    for flac_path in flac_files:
        wav_path = os.path.splitext(flac_path)[0] + '.wav'
        if path.exists(wav_path):
            rel_path = path.relpath(wav_path, base_dir)
            all_wavs.append((wav_path, rel_path))

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
            save_last_processed_data(base_dir, full_path, indices)

            if update_callback:
                update_callback(processed_count)

        except Exception as e:
            print(f"Error procesando {full_path}: {e}")
            return

    reset_progress()