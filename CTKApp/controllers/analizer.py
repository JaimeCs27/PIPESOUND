import yaml
import datetime
from os import path, fsync

from .compute_indice import *
from .acoustic_index import *

INDICES = 'Indices'
ARG = 'arguments'
SPECTR = 'spectro'

class Analizer:
    def __init__(self, config_file):
        print(config_file)
        with open(config_file, 'r') as stream:
            self.config = yaml.load(stream, Loader=yaml.FullLoader)

    '''
    Esta función se encarga de aplicar todos los filtros seleccionados a un archivo .WAV
    Entradas:
        - file: Archivo de audio
        - indices: Una lista de indices seleccionados por el usuario
    Salidas:
        No tiene
    ''' 
    def process_audio_file(self, file, indices):
        for index in indices:
            if index == 'Acoustic_Complexity_Index':
                self.Acoustic_complexity_index(file)
            elif index == 'Bio_acoustic_Index':
                self.Bioacustic_index(file)
            elif index == 'Acoustic_Diversity_Index':
                self.Acoustic_Diversity_Index(file)
            elif index == 'Acoustic_Evenness_Index':
                self.Acoustic_Evenness_Index(file)
            elif index == 'Spectral_Entropy':
                self.Spectral_Entropy(file)
            elif index == 'Normalized_Difference_Sound_Index':
                self.Normalized_Difference_Sound_Index(file)
            elif index == 'NB_peaks':
                self.NB_peaks(file)
            elif index == 'Temporal_Entropy':
                self.Temporal_Entropy(file)
            elif index == 'Wave_Signal_To_Noise_Ratio':
                self.Wave_Signal_To_Noise_Ratio(file)
    '''
    Esta funcion se encarga de obtener los atributos/parametros de la configuracion y realida el analisis Spectral de entropia
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Spectral_Entropy(self, file):
        index = 'Spectral_Entropy'
        spectro, _ = compute_spectrogram(file, **self.config[INDICES][index][SPECTR])
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(spectro)
        file.indices[index] = Index(index, main_value=main_value)
           

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis bioacustico
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Bioacustic_index(self, file):
        index = 'Bio_acoustic_Index'
        spectro, frequencies = compute_spectrogram(file, **self.config[INDICES][index][SPECTR])
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(spectro, frequencies, **self.config[INDICES][index][ARG])
        file.indices[index] = Index(index, main_value=main_value)

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Acoustic_complexity_index(self, file):
        index = 'Acoustic_Complexity_Index'
        spectro, _ = compute_spectrogram(file, **self.config[INDICES][index][SPECTR])
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        j_bin = int(self.config[INDICES][index][ARG]["j_bin"] * file.sr / self.config[INDICES][index][SPECTR]['windowHop'])
        main_value, temporal_values = methodToCall(spectro, j_bin)
        file.indices[index] = Index(index, temporal_values=temporal_values, main_value=main_value)

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el analisis para el indice: Acoustic Diversity
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    
    def Acoustic_Diversity_Index(self, file):
        index = 'Acoustic_Diversity_Index'
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        freq_band_Hz = self.config[INDICES][index][ARG]['max_freq'] / self.config[INDICES][index][ARG]['freq_step']
        windowLength = int(file.sr / freq_band_Hz)
        spectro, _ = compute_spectrogram(file, windowLength=windowLength, windowHop=windowLength, scale_audio=True, square=False, windowType='hann', centered=False, normalized=False)
        main_value = methodToCall(spectro, freq_band_Hz, **self.config[INDICES][index][ARG])
        file.indices[index] = Index(index, main_value=main_value)


    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración de y realiza el análisis
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Acoustic_Evenness_Index(self, file):
        index = 'Acoustic_Evenness_Index'
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        freq_band_Hz = self.config[INDICES][index][ARG]['max_freq'] / self.config[INDICES][index][ARG]['freq_step']
        windowLength = int(file.sr / freq_band_Hz)
        spectro, _ = compute_spectrogram(
            file,
            windowLength=windowLength,
            windowHop=windowLength,
            scale_audio=True,
            square=False,
            windowType='hann',
            centered=False,
            normalized=False
        )
        main_value = methodToCall(spectro, freq_band_Hz, **self.config[INDICES][index][ARG])
        file.indices[index] = Index(index, main_value=main_value)

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis para el índice: Normalized Difference Sound Index (NDSI)
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Normalized_Difference_Sound_Index(self, file):
        index = 'Normalized_Difference_Sound_Index'
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(file, **self.config[INDICES][index]['arguments'])
        file.indices[index] = Index(index, main_value=main_value)

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis para el índice: Normalized Difference Sound Index (NDSI)
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def NB_peaks(self, file):
        index = 'NB_peaks'
        spectro, frequencies = compute_spectrogram(file, **self.config[INDICES][index][SPECTR])
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(spectro, frequencies, **self.config[INDICES][index][ARG])
        file.indices[index] = Index(index, main_value=main_value)
    
    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis para el índice: Temporal Entropy
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Temporal_Entropy(self, file):
        index = 'Temporal_Entropy'
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(file, **self.config[INDICES][index][ARG])
        file.indices[index] = Index(index, main_value=main_value)

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análisis para el índice: Wave Signal To Noise Ratio (WSNR)
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Wave_Signal_To_Noise_Ratio(self, file):
        index = 'Wave_SNR'
        methodToCall = globals().get(self.config[INDICES][index]['function'])
        main_value = methodToCall(file, **self.config[INDICES][index][ARG])
        processed_values = {
            'name': index,
            'main_value': main_value['SNR']  # Extraer el valor principal
            # 'Acoustic_activity': main_value['Acoustic_activity'],
            # 'Count_acoustic_events': main_value['Count_acoustic_events'],
            # 'Average_duration': main_value['Average_duration']
        }
        file.indices[index] = Index(**processed_values)


    '''
    Esta función se encarga de escribir en el archivo csv los datos recopilados del análisis
    Entradas:
        - file: Archivo de audio
        - project_name: Nombre del proyecto analizado
        - site: Nombre del site analizado
        - csv_path: Dirección donde está ubicado el csv
    Salidas
        No tiene
    '''
    def write_to_csv(self, file, project_name, site, csv_path):
        result = ''
        date = datetime.datetime.fromtimestamp(path.getctime(file.file_path))
        format_date = date.strftime("%Y-%m-%d")
        format_hour = date.strftime('%H:%M:%S')
        values = [project_name,site, format_date,format_hour, file.file_name]
        keys = ['project_name', 'site', 'date', 'time', 'filename']
        for index, Index in file.indices.items():
            for key, value in Index.__dict__.items():
                if key != 'name':
                    keys.append(index + "_" + key)
                    values.append(float(value))
        for value in values:
            result += str(value) + ','
        result += '\n'
        with open(csv_path, "a", newline="") as f:
            f.write(result)
            f.flush()  # Fuerza la escritura en disco
            fsync(f.fileno())  # Asegura que los datos se guarden físicamente

    def create_temp_file(self, file, project_name, site, temp_path):
        temp_path = path.join(temp_path, file.file_name + ".txt")
        result = ''
        date = datetime.datetime.fromtimestamp(path.getctime(file.file_path))
        format_date = date.strftime("%Y-%m-%d")
        format_hour = date.strftime('%H:%M:%S')
        values = [project_name, site, format_date, format_hour, file.file_name]
        keys = ['project_name', 'site', 'date', 'time', 'filename']
        for index, Index in file.indices.items():
            for key, value in Index.__dict__.items():
                if key != 'name':
                    keys.append(index + "_" + key)
                    values.append(float(value))
        result = ''
        for value in values:
            result += str(value) + ','
        result += '\n'
        with open(temp_path, "a", newline="") as f:
            f.write(result)
            f.flush()
            fsync(f.fileno())


    def set_headers(self, indices, csv_path):
        if not path.exists(csv_path):
            keys = 'project_name, site, date, time, filename,'
            for index in indices:
                keys += (index + '_main_value,')
                if index == 'Acoustic_Complexity_Index':
                    keys += (index + "_min,")
                    keys += (index + "_max,")
                    keys += (index + "_mean,")
                    keys += (index + "_median,")
                    keys += (index + "_std,")
                    keys += (index + "_var,")
                if index == 'Wave_SNR':
                    keys += (index + "_SNR,")
                    keys += (index + "_Acoustic_activity,")
                    keys += (index + "_Count_acoustic_events,")
                    keys += (index + "_Average_duration,")
            keys += '\n'
            with open(csv_path, "w", newline="") as f:
                f.write(keys)
                f.flush()  # Fuerza la escritura en disco
                fsync(f.fileno())  # Asegura que los datos se guarden físicamente
        
