from .rfcx import client
import datetime
from os import makedirs

class ArbimonModule:
    def __init__(self):
        self.client = None

    '''
    Esta función se encarga de autenticar el usuario de arbimon y crea el cliente
    '''
    def Authenticate(self):
        self.client = client.Client()
        self.client.authenticate()

    '''
    Esta funcion retorna los proyectos del usuario de arbimon autenticado
    Entradas:
        - No tiene
    Salidas:
        - Una lista de jsons con los proyectos
    '''
    def Load_projects(self):
        return self.client.projects()
    
    '''
    Esta funcion retorna los proyectos del usuario de arbimon autenticado
    Entradas:
        - project_id: String con el id del proyecto
    Salidas:
        - Una lista de jsons con los sites
    '''
    def Load_Sites(self, project_id):
        return self.client.streams(projects=project_id)
    
    '''
    Esta funcion recibe una lista de sites de un proyecto, se encarga de descargarlos y crea un directorio donde guardarlos
    Entradas
        - sites: lista<json> sites que debe descargar
        - folder_path: string folder que el usuario eligio donde guardar los audios
        - project_name: string nombre del proyecto
        - start: datetime fecha de inicio, su valor por defecto es el 1/1/1930
        - end: datetime fecha de fin, su valor por defecto es la fecha actual
    Salidas:
        No posee
    '''
    def Download_Project(self, sites, folder_path, project_name, start=datetime.datetime(1930, 1, 1), end=datetime.datetime.today()):
        full_path = folder_path +"/"+ project_name
        self.Create_folder_for_project(full_path)
        for site in sites:
            try:
                self.Download_Site(site, full_path, start, end)
            except Exception as e:
                print("Error while downloading site " + site["name"] + ": " + str(e))
                raise Exception(f"Error downloading site {site['name']} ({site['id']}): {str(e)}") from e

    '''
    Esta funcion se encarga de descargar los audios de un site en una carpeta local
    Entrada:
        - site: json con la informacion del site
        - folder_path: String ruta donde se almacenaran los audios
        - start: datetime fecha de inicio de los audios
        - end: datetime fecha final de los audios
    Salida:
        No posee
    '''
    def Download_Site(self, site, folder_path, start, end):
        try:
            if self.client == None:
                raise Exception("Client not found")
            self.client.download_segments(site["id"],folder_path, start, end, file_ext="flac")
        except Exception as e:
            raise Exception(f"Download interrupted for site {site['id']}") from e

    
    def Create_folder_for_project(self, full_path):
        try:
            makedirs(full_path)
            print(f"Directory '{full_path}' created successfully.")
        except FileExistsError:
            print(f"Directory '{full_path}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{full_path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")



