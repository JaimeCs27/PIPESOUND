from compute_indice import *
from acoustic_index import *
import yaml
from os import path, fsync
import datetime

INDICES = 'Indices'
ARG = 'arguments'
SPECTR = 'spectro'

class Analizer:
    def __init__(self, config_file):
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
            elif index == 'Acoustic_Evenness_Index':
                self.Acoustic_Evenness_Index(file)

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
        for index, Index in file.indices.items():
            for key, value in Index.__dict__.items():
                if key != 'name':
                    values.append(float(value))
        for value in values:
            result += str(value) + ','
        result += '\n'
        print(result)
        # with open(csv_path, "a", newline="") as f:
        #     f.write(result)
        #     f.flush()  # Fuerza la escritura en disco
        #     fsync(f.fileno())  # Asegura que los datos se guarden físicamente
        
