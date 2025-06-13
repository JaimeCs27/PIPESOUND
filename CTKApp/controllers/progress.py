import json
import threading
import multiprocessing as mp
import time
import os
import psutil
import soundfile as sf
from scipy import signal
from os import walk, path
import librosa
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .acoustic_index import *
import multiprocessing as mp


PROGRESS_PATH = path.join(path.dirname(__file__), '..', 'views', 'temp_audio_files')


class Process(mp.Process):
    def __init__(self, id, full_path, rel_path, analizer, indices, temp_path, project_name, site, stop_event):
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
        self.stop_event = stop_event
        
        
    
    def run(self):
        try:
            if self.stop_event.is_set():
                reset_progress()
                return
            file = AudioFile(self.full_path, True)
            self.analizer.process_audio_file(file, self.indices)
            self.analizer.create_temp_file(file, self.project_name, self.site, self.temp_path)
            #print(f"Proceso {self.id} completado para {self.full_path}")
            if self.counter and self.lock:
                with self.lock:
                    self.counter.value += 1
            if self.stop_event.is_set():
                reset_progress()
                return
        except Exception as e:
            print(f"Error processing {self.full_path}: {e}")



def load_last_processed_data():
    """Revisa la carpeta temp_audio_files para revisar si hay archivos temporales."""
    print(PROGRESS_PATH)
    if path.exists(PROGRESS_PATH):
        temp_files = [f for f in os.listdir(PROGRESS_PATH) if f.endswith('.txt')]
        if len(temp_files) == 0:
            print("No temporary files found to process.")
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

def kill_all(processes, grace=0.5):
    """
    Mata *todo* el árbol de procesos que cuelga de la lista «processes».
    1) SIGTERM  → chance de apagado limpio
    2) espera ‹grace› segundos
    3) SIGKILL / .kill() a lo que siga vivo
    """
    import signal, time, psutil, os

    # ---- 1. Construir la lista [padres + descendientes] -----------------
    proc_tree = []
    for p in processes:
        if not p.is_alive():
            continue
        try:
            parent = psutil.Process(p.pid)
            proc_tree.append(parent)
            proc_tree.extend(parent.children(recursive=True))
        except psutil.NoSuchProcess:
            pass          # ya murió

    if not proc_tree:
        return            # nada que matar

    # ---- 2. SIGTERM (terminate) a todos ---------------------------------
    for pr in proc_tree:
        try:
            pr.terminate()
        except psutil.NoSuchProcess:
            pass

    # ---- 3. Espera «grace» ---------------------------------------------
    gone, alive = psutil.wait_procs(proc_tree, timeout=grace)

    # ---- 4. SIGKILL / kill a lo que quede -------------------------------
    for pr in alive:
        try:
            pr.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(alive, timeout=grace)

    # ---- 5. join() a tus mp.Process para que no queden zombis -----------
    for p in processes:
        if p.is_alive():
            p.join()

def convert_to_wav(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.flac', '.mp3']:
        try:
            data, samplerate = librosa.load(file_path, sr=None)  # Preserve original sample rate
            wav_path = os.path.splitext(file_path)[0] + '.wav'
            sf.write(wav_path, data, samplerate)
            print(f'File converted and saved as: {wav_path}')

            os.remove(file_path)
            print(f'Original file deleted: {file_path}')

        except Exception as e:
            print(f"Error converting {file_path}: {e}")

def combine_temp_files_to_csv(temp_path, csv_path):
    """
    Combines all .txt files in temp_path into a single CSV file.
    """
    if not path.exists(temp_path):
        print(f"The temporary folder {temp_path} does not exist.")
        return

    temp_files = [f for f in os.listdir(temp_path) if f.endswith('.txt')]

    if not temp_files:
        print("No temporary files found to combine.")
        return

    # Create headers if the CSV file does not exist
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

    print(f"All temporary files have been combined into {csv_path}.")

def monitor_temp_files(update_callback, total_files, counter, stop_event):
    """
    Monitors the number of files in the temp_audio_files folder and updates the progress using the callback.
    """
    while True:
        if stop_event and stop_event.is_set():
            print("Monitoring stopped.")
            break
        with counter.get_lock():  # Ensures safe access to the counter
            current_count = counter.value
        if update_callback:
            update_callback(current_count, total_files)
        time.sleep(1.5)  # Wait for 1.5 seconds before checking again
        if current_count >= total_files:
            print("All files have been processed.")
            break


def analize(base_dir, analizer, indices, csv_path, temp_path, resume_from=None, stop_event=None, update_callback=None):
    """Analyzes the audio files in base_dir and updates the progress immediately."""
    resume = resume_from is not None
    should_skip = True
    if stop_event and stop_event.is_set():
        print("Analysis stopped before starting the process.")
        return

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
        # Create indices.json
        with open(path.join(temp_path, "temp_data.json"), 'w') as f:
            data = {
                "indices": indices,
                "base_dir": base_dir
                }
            json.dump(data, f)
    all_wavs = []
    flac_files = []
    supported_formats = ['.WAV', '.Flac', '.flac', '.FLAC', '.MP3', '.mp3']

    # Recopilar rutas de archivos .wav y .flac
    for root, _, files in walk(base_dir):
        for filename in sorted(files):
            full_path = path.join(root, filename)
            if filename.endswith('.wav'):
                rel_path = path.relpath(full_path, base_dir)
                all_wavs.append((full_path, rel_path))
            elif any(filename.endswith(ext) for ext in supported_formats):
                flac_files.append(full_path)
            else:
                print(f"Format not supported: {filename}")


    print(f"Files found to process: {len(all_wavs)}")

    # Convert .flac files to .wav in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(convert_to_wav, flac_files)

    # Add new .wav files generated by the conversion
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

    print(f"Total files to process: {total_files}")

    counter = mp.Value('i', 0)
    lock = mp.Lock()

    # Iniciar el monitor de archivos temporales
    monitor_thread = threading.Thread(
        target=monitor_temp_files,
        args=(update_callback, total_files, counter, stop_event),  # Pasa counter como argumento
        daemon=True
    )
    monitor_thread.start()


    project_name = path.basename(base_dir)

    # This code is parallel

    processes = []
    max_processes = max(1, mp.cpu_count() - 1)  # Limit based on available cores
    i = 0

    while i < len(all_wavs) or any(p.is_alive() for p in processes):
        # Remove finished processes from the list
        processes = [p for p in processes if p.is_alive()]

        # Spawn new processes if there is room
        while len(processes) < max_processes and i < len(all_wavs):
            if stop_event and stop_event.is_set():
                print("Analysis stopped during process spawning.")
                kill_all(processes, grace=0.5)
                reset_progress()
                return

            full_path, rel_path = all_wavs[i]
            process = Process(
                i, full_path, rel_path, analizer, indices, temp_path,
                project_name, path.basename(path.dirname(full_path)), stop_event
            )
            process.counter = counter
            process.lock = lock
            process.daemon = True
            process.start()
            processes.append(process)
            i += 1

        time.sleep(0.1)  # Prevent busy waiting

    # After all processes are done or stop_event triggered
    if stop_event and stop_event.is_set():
        print("Analysis stopped before completion.")
        reset_progress()
        return

    print("All parallel processes have finished.")

    # Combine temporary result files into one CSV
    combine_temp_files_to_csv(temp_path, csv_path)

    # Clean up temporary files
    reset_progress()
