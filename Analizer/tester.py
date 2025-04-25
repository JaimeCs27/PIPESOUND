from scipy import signal
from os import walk, path
from datetime import datetime
import os
from ArbimonModule import ArbimonModule

def test():
    arbModule = ArbimonModule()
    project = None
    try:
        project = arbModule.Load_projects()[0]
    except:
        print("Error loading user projects.")
    sites = None
    try:
        sites = arbModule.Load_Sites(project['id'])
        for site in sites:
            print(site['name'])
    except:
        print("Error while loading " +project['name'] + " sites")

    try:
        arbModule.Download_Project(sites, "D:/Universidad/Semestre VII/Proyecto/PIPESOUND/Prueba", "Proyecto 1")
    except:
        print("Error while Downloading the files")




test()
