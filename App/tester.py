from scipy import signal
from os import walk, path
from datetime import datetime
import os
import sys


# Agrega la carpeta 'app' al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ArbimonWindow import ArbimonWindow

def test():
    window = ArbimonWindow()
    window.mainloop()



test()
