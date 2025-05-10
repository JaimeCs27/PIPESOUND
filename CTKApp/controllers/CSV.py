import csv
from .acoustic_index import Index


class Audio():
    def __init__(self, name, indices):
        self.name = name
        self.indices = indices

class Site():
    def __init__(self, name, audios):
        self.audios = audios
        self.name = name

    def get_indices(self):
        indices = []
        for index in self.audios[0].indices:
            indices.append(index.name)
        return indices

class CSV():
    def __init__(self, file):
        self.sites = []
        self.create_json(file)
    
    def indices_in_file(self):
        return self.sites[0].get_indices()
    
    def create_json(self, file):
        site_dict = {}  # clave: nombre del sitio, valor: dict de audios

        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            index_columns = [col for col in reader.fieldnames if col.endswith('_main_value')]

            for row in reader:
                site_name = row["site"]
                audio_name = row["filename"]

                # Crear todos los índices dinámicamente desde las columnas *_main_value
                indices = []
                for col in index_columns:
                    index_name = col.replace("_main_value", "")
                    value = row[col]
                    if value.strip() != "":
                        indices.append(Index(index_name, main_value=value))

                audio = Audio(audio_name, indices)

                if site_name not in site_dict:
                    site_dict[site_name] = {}

                # Evita duplicar audios con el mismo nombre
                if audio_name not in site_dict[site_name]:
                    site_dict[site_name][audio_name] = audio

            # Crear objetos Site con su lista de audios
            for site_name, audios_dict in site_dict.items():
                audios = list(audios_dict.values())
                self.sites.append(Site(site_name, audios))
