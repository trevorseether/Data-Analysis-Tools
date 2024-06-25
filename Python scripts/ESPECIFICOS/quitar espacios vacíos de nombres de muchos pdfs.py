# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 18:10:38 2024

@author: sanmiguel38
"""

import os

# Ruta de la carpeta donde están los archivos PDF
ruta_carpeta = 'C:\\Users\\sanmiguel38\\Desktop\\inactivos prueba\\INACTIVOS'

# Obtener la lista de archivos en la carpeta
archivos = os.listdir(ruta_carpeta)

# Recorrer cada archivo
for archivo in archivos:
    # Obtener el nombre completo del archivo con la ruta
    nombre_original = os.path.join(ruta_carpeta, archivo)
    
    # Verificar si es un archivo PDF
    if archivo.lower().endswith('.pdf'):
        # Eliminar espacios adicionales en el nombre del archivo
        nombre_nuevo = ' '.join(archivo.split())
        
        # Renombrar el archivo solo si el nombre ha cambiado
        if nombre_nuevo != archivo:
            nuevo_nombre_completo = os.path.join(ruta_carpeta, nombre_nuevo)
            os.rename(nombre_original, nuevo_nombre_completo)
            print(f'Renombrado: {archivo} -> {nombre_nuevo}')
        else:
            print(f'No se modificó: {archivo}')
    else:
        print(f'No es un archivo PDF: {archivo}')


