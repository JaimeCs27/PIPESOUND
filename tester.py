from Analizer import Analizer
from acoustic_index import *

def test():
    analizer = Analizer('config/config.yaml')
    file = AudioFile('Test_audios/1.wav', True)
    analizer.process_audio_file(file, ['Acoustic_Complexity_Index', 'Bio_acoustic_Index', 'Acoutic_Diversity_Index' 'Acoustic_Evenness_Index'])
    analizer.write_to_csv(file, "project a", 'site 1', "prueba.csv")

test()