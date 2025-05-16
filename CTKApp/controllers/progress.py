import json
import threading
import multiprocessing as mp
import time
import os
import soundfile as sf
from scipy import signal
from os import walk, path, remove
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .acoustic_index import *


PROGRESS_PATH = path.join(path.dirname(__file__), '..', 'views', 'temp_audio_files')


class Process(mp.Process):
    def __init__(self, id, full_path, rel_path, analizer, indices, temp_path, project_name, site):
        super(Process, self).__init__()
        self.full_path = full_path
        self.rel_path = rel_path
        self.id = id
        self.analizer = analizer
        self.indices = indices
        self.temp_path = temp_path
        self.project_name = project_name
        self.site = site
        self.counter = None
        self.lock = None
        
    
    def run(self):
        try:
            file = AudioFile(self.full_path, True)
            self.analizer.process_audio_file(file, self.indices)
            self.analizer.create_temp_file(file, self.project_name, self.site, self.temp_path)
            #print(f"Proceso {self.id} completado para {self.full_path}")
            if self.counter and self.lock:
                with self.lock:
                    self.counter.value += 1
        except Exception as e:
            print(f"Error procesando {self.full_path}: {e}")



def load_last_processed_data():
    """Revisa la carpeta temp_audio_files para revisar si hay archivos temporales."""
    print(PROGRESS_PATH)
    if path.exists(PROGRESS_PATH):
        temp_files = [f for f in os.listdir(PROGRESS_PATH) if f.endswith('.txt')]
        if len(temp_files) == 0:
            print("No hay archivos temporales para procesar.")
            return None
        json_data = [f for f in os.listdir(PROGRESS_PATH) if f.endswith('.json')]
        print(json_data)
        with open(path.join(PROGRESS_PATH, json_data[0]), 'r') as f:
            data = json.load(f)
        return {
            "root": data['base_dir'],
            "file": temp_files,
            "indices": data['indices']
        }
    return None

def reset_progress():
    """Elimina el archivo de progreso."""
    if path.exists(PROGRESS_PATH):
        temp_files = [f for f in os.listdir(PROGRESS_PATH)]
        for temp_file in temp_files:
            temp_file_path = path.join(PROGRESS_PATH, temp_file)
            os.remove(temp_file_path)

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

def combine_temp_files_to_csv(temp_path, csv_path):
    """
    Combina todos los archivos .txt en temp_path en un único archivo CSV.
    """
    if not path.exists(temp_path):
        print(f"La carpeta temporal {temp_path} no existe.")
        return

    temp_files = [f for f in os.listdir(temp_path) if f.endswith('.txt')]

    if not temp_files:
        print("No se encontraron archivos temporales para combinar.")
        return

    # Crear encabezados si el archivo CSV no existe
    if not path.exists(csv_path):
        with open(csv_path, "w", newline="") as csv_file:
            csv_file.write("project_name,site,date,time,filename,indices\n")

    # Leer cada archivo temporal y agregar su contenido al CSV
    with open(csv_path, "a", newline="") as csv_file:
        for temp_file in temp_files:
            temp_file_path = path.join(temp_path, temp_file)
            with open(temp_file_path, "r") as temp:
                csv_file.write(temp.read())
            #print(f"Archivo {temp_file} unido al CSV.")

    print(f"Todos los archivos temporales se han combinado en {csv_path}.")

def monitor_temp_files(update_callback, total_files, counter):
    """
    Monitorea la cantidad de archivos en la carpeta temp_audio_files y actualiza el progreso usando el callback.
    """
    while True:
        with counter.get_lock():  # Asegura acceso seguro al contador
            current_count = counter.value
        if update_callback:
            update_callback(current_count, total_files)
        time.sleep(1.5)  # Esperar 0.5 segundos antes de volver a consultar
        if current_count >= total_files:
            print("Todos los archivos han sido procesados.")
            break


def analize(base_dir, analizer, indices, csv_path, temp_path, resume_from=None, stop_flag=None, update_callback=None):
    """Analiza los archivos de audio en base_dir y actualiza el progreso inmediatamente."""
    resume = resume_from is not None
    should_skip = True
    if not path.exists(temp_path):
        os.makedirs(temp_path)
    temp_files = [f for f in os.listdir(temp_path) if f.endswith('.txt')]
    if (len(temp_files) > 0):
        if resume:
            last_processed = load_last_processed_data()
            if last_processed:
                base_dir = last_processed['root']
                resume_from = last_processed['file']
                indices = last_processed['indices']
    else:
        "Crear archivo indices.json"
        with open(path.join(temp_path, "temp_data.json"), 'w') as f:
            data = {
                "indices": indices,
                "base_dir": base_dir
                }
            json.dump(data, f)
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

    print(f"Archivos encontrados para procesar: {len(all_wavs)}")

    # Convertir archivos .flac a .wav en paralelo
    with ThreadPoolExecutor() as executor:
        executor.map(convert_to_wav, flac_files)

    # Agregar archivos .wav nuevos generados por la conversión
    for flac_path in flac_files:
        wav_path = os.path.splitext(flac_path)[0] + '.wav'
        if path.exists(wav_path):
            rel_path = path.relpath(wav_path, base_dir)
            all_wavs.append((wav_path, rel_path))

    if resume_from:
        processed_files = {path.splitext(f)[0] for f in resume_from}
        all_wavs = [(full_path, rel_path) for full_path, rel_path in all_wavs if rel_path not in processed_files]

    processed_count = 0
    total_files = len(all_wavs)

    print(f"Total de archivos a procesar: {total_files}")

    counter = mp.Value('i', 0)
    lock = mp.Lock()

    # Iniciar el monitor de archivos temporales
    monitor_thread = threading.Thread(
        target=monitor_temp_files,
        args=(update_callback, total_files, counter),  # Pasa counter como argumento
        daemon=True
    )
    monitor_thread.start()


    project_name = path.basename(base_dir)

    # Este codigo es paralelo
    processes = []
    for i, (full_path, rel_path) in enumerate(all_wavs):
        process = Process(i, full_path, rel_path, analizer, indices, temp_path, project_name, path.basename(path.dirname(full_path)))
        process.counter = counter
        process.lock = lock
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print("Todos los procesos paralelos han terminado.")

    # Unir temp files en un solo archivo CSV
    combine_temp_files_to_csv(temp_path, csv_path)

    # Eliminar archivos temporales
    reset_progress()