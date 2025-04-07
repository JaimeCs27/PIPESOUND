from os import path
import os

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

