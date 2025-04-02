# Script para analisis de Sonidos
# Elaborado por: Roberto Vargas Masis
# Version 1.0
# Ultima actualizacion 10/03/2025


########################################################################################
#######################           ANALISIS           ###################################


#Establecer el directorio de trabajo y revisar directorio de trabajo
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/PIPESOUND/Test_audios")
getwd()

#Instalar paquetes necesarios (agregar aqui los que vayan necesitando)
install.packages("devtools")
install.packages("Rcpp")
install.packages("seewave")
install.packages("testthat")
install.packages("vegan")
install.packages("rlang")
install.packages("dplyr")
install.packages("bioacoustics")
install.packages("gridExtra")
install.packages("grid")
install.packages("ggplot2")
install.packages("lattice")
install.packages("tuneR")
install.packages("tidyr", dependencies = T)    # Datos ordenados. lo agregue para poder separae la fecha de la hora
install.packages("reshape")
install.packages("ggpubr")
install.packages("wesanderson")

#Llamar los paquetes necesarios (agregar aqui los que vayan necesitando)
library(devtools)
library(Rcpp)
library(seewave)
library(testthat)
library(vegan)
library(rlang)
library(dplyr)
library(bioacoustics)
library(grid)
library(gridExtra)
library(ggplot2)
library(lattice)
library(tuneR)
library(tidyr)
library(reshape)
library(ggpubr)
library(wesanderson)

#Instalacion de SINAX Version 1.3
install_github("osoramirez/Sinax") # Forma 1

# Llamar Sinax y resumeRdesc
library(Sinax)

############################### Analisis de indices ###########################################

# Crear un vector de la lista de las rutas de las carpetas en el directorio de manera recursiva
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/PIPESOUND/Test_audios")
getwd()
l1 <- list.dirs(path = ".", recursive = F, full.names = T)
l1

#Crear un vector de una lista recursiva de las carpetas en el directorio
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/PIPESOUND/Test_audios")
getwd()
p1 <- list.files()
p1

#Carpeta por carpeta con nombres de la ruta en el directorio
x = 1
pre = list()
for (i in p1) {
  print(p1[x])
  setwd(p1[x])
  pre[[x]] = soundindex10()
  pre[[x]]["Sitio"] <- i 
  x = x+1
  setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/Prueba")
}  

#Vista de las dataframe realizadas
View(pre[[1]])


#Unir las dataframe en una sola ** Las dataframe deben tener los mismos nombres en columnas
pres <- rbind(pre[[1]], pre[[2]], pre[[3]], pre[[4]], pre[[5]])
View(pres)

#Crear el csv con todos los datos
write.csv(pres, file = "prueba.csv")