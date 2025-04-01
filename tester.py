from Analizer import Analizer
from acoustic_index import *
import yaml
from scipy import signal

def test():

    analizer = Analizer('config/config.yaml')
    
    file = AudioFile('Test_audios/1.wav', True)
    
    yml_file = 'config/config.yaml'
    with open(yml_file, 'r') as stream:
        data_config = yaml.load(stream, Loader=yaml.FullLoader)
    if data_config['Filtering']['type'] == 'butterworth':
        print('- Pre-processing - High-Pass Filtering:', data_config['Filtering'])
        freq_filter = data_config['Filtering']['frequency']
        Wn = freq_filter/float(file.niquist)
        order = data_config['Filtering']['order']
        [b,a] = signal.butter(order, Wn, btype='highpass')
        # to plot the frequency response
        #w, h = signal.freqz(b, a, worN=2000)
        #plt.plot((file.sr * 0.5 / np.pi) * w, abs(h))
        #plt.show()
        file.process_filtering(signal.filtfilt(b, a, file.sig_float))
    elif data_config['Filtering']['type'] == 'windowed_sinc':
        print('- Pre-processing - High-Pass Filtering:', data_config['Filtering'])
        freq_filter = data_config['Filtering']['frequency']
        fc = freq_filter / float(file.sr)
        roll_off = data_config['Filtering']['roll_off']
        b = roll_off / float(file.sr)
        N = int(np.ceil((4 / b)))
        if not N % 2: N += 1  # Make sure that N is odd.
        n = np.arange(N)
        # Compute a low-pass filter.
        h = np.sinc(2 * fc * (n - (N - 1) / 2.))
        w = np.blackman(N)
        h = h * w
        h = h / np.sum(h)
        # Create a high-pass filter from the low-pass filter through spectral inversion.
        h = -h
        h[(N - 1) / 2] += 1
        file.process_filtering(np.convolve(file.sig_float, h))
    analizer.process_audio_file(file, ['Acoustic_Complexity_Index', 'Bio_acoustic_Index', 'Acoutic_Diversity_Index', 'Acoustic_Evenness_Index', 'Normalized_Difference_Sound_Index', 'Spectral_Entropy'])
    analizer.write_to_csv(file, "project a", 'site 1', "prueba.csv")

test()