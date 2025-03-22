from compute_indice import *
from acoustic_index import *
import yaml
from os import path, fsync
import datetime

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

    '''
    Esta función se encarga de obtener los atributos/parámetros de la configuración y realiza el análsis
    Entradas:
        - File: Archivo de audio
    Salidas:
        No tiene
    '''
    def Acoustic_complexity_index(self, file):
        index = 'Acoustic_Complexity_Index'
        spectro, _ = compute_spectrogram(file, **self.config['Indices'][index]['spectro'])
        methodToCall = globals().get(self.config['Indices'][index]['function'])
        j_bin = int(self.config['Indices'][index]['arguments']["j_bin"] * file.sr / self.config['Indices'][index]['spectro']['windowHop'])
        main_value, temporal_values = methodToCall(spectro, j_bin)
        file.indices[index] = Index(index, temporal_values=temporal_values, main_value=main_value)
    
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
        # with open(csv_path, "a", newline="") as f:
        #     f.write(result)
        #     f.flush()  # Fuerza la escritura en disco
        #     fsync(f.fileno())  # Asegura que los datos se guarden físicamente
        
