# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:21:30 2024

@author: sanmiguel38
"""

import pandas as pd
import shutil
import os
# os.chdir('R:\\REPORTES DE GESTIÓN\\Insumo para Analisis\\CHERNANDEZ\\certificados de depositos\\inactivos')

# Ejemplo de DataFrame con nombres de archivos
# data = {'archivo': [ 'asd.pdf', 'sdf.pdf', 'dfg.pdf']}
# df = pd.DataFrame(data)

ubi     = 'C:\\Users\\sanmiguel38\\Desktop\\inactivos prueba'
archivo = 'Inactivos grupo 6.xlsx'
df = pd.read_excel(io = ubi + '\\' + archivo)

# Directorio de origen y destino
directorio_origen  = 'C:\\Users\\sanmiguel38\\Desktop\\inactivos prueba\\encontrados'
directorio_destino = 'C:\\Users\\sanmiguel38\\Desktop\\inactivos prueba\\G6'

# Asegúrate de que el directorio de destino existe
os.makedirs(directorio_destino, exist_ok=True)

conteo = 1
no_encontrados = []
# Iterar sobre los nombres de archivo en el DataFrame
for nombre_archivo in df['Nombre pdf']:
    ruta_origen = os.path.join(directorio_origen, nombre_archivo)
    ruta_destino = os.path.join(directorio_destino, nombre_archivo)
    
    # Comprobar si el archivo existe en el directorio de origen
    if os.path.exists(ruta_origen):
        # Mover el archivo al directorio de destino
        shutil.move(ruta_origen, ruta_destino)
        print(f"Movido: {nombre_archivo} a {directorio_destino}")
        
        print(conteo)
        conteo += 1
    else:
        print(f"Archivo no encontrado: {nombre_archivo}")
        no_encontrados.append(nombre_archivo)

print("Proceso completado.")

if len(no_encontrados) > 0:
    print('los siguientes archivos no fueron encontrados')
    print(no_encontrados)
