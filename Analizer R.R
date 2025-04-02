# Script para analisis de Sonidos
# Elaborado por: Roberto Vargas Masis
# Version 1.0
# Ultima actualizacion 10/03/2025


########################################################################################
#######################           ANALISIS           ###################################


#Establecer el directorio de trabajo y revisar directorio de trabajo
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto")
getwd()

#Instalar paquetes necesarios (agregar aqui los que vayan necesitando)
#install.packages("devtools")
#install.packages("Rcpp")
#install.packages("seewave")
#install.packages("testthat")
#install.packages("vegan")
#install.packages("rlang")
#install.packages("dplyr")
#install.packages("bioacoustics")
#install.packages("gridExtra")
#install.packages("grid")
#install.packages("ggplot2")
#install.packages("lattice")
#install.packages("tuneR")
#install.packages("tidyr", dependencies = T)    # Datos ordenados. lo agregue para poder separae la fecha de la hora
#install.packages("reshape")
#install.packages("ggpubr")
#install.packages("wesanderson")

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
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto")
getwd()
l1 <- list.dirs(path = ".", recursive = F, full.names = T)
l1

#Crear un vector de una lista recursiva de las carpetas en el directorio
setwd("C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/PIPESOUND/Test_audios")
getwd()
p1 <- list.files()
p1

# Directorio base donde están los archivos wav
base_dir <- "C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/PIPESOUND/Test_audios"

# Ejecutar soundindex1() solo una vez
sound_result <- soundindex1()  # Esto hace el procesamiento de todos los archivos

# Crear un vector con los nombres de los archivos
file_names <- p1

# Asignar el nombre del archivo a la columna "Sitio" en cada fila
x = 1
for (i in file_names) {
  sound_result$Sitio <- i  # Asigna el nombre del archivo a la columna "Sitio"
  pre[[x]] <- sound_result  # Almacena el resultado en la lista
  x = x + 1
}

# Unir todas las dataframes en una sola
pres <- do.call(rbind, pre)

# Vista de la dataframe combinada
View(pres)

# Crear el csv con todos los datos
write.csv(pres, file = "C:/Users/sebas/OneDrive/TEC/Semestre 1 2025/Proyecto/Prueba/prueba.csv")


