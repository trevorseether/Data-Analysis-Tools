# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:27:46 2024

@author: sanmiguel38
"""

import os

# Ruta a la carpeta con los archivos PDF
carpeta = 'R:\\REPORTES DE GESTIÓN\\Insumo para Analisis\\CHERNANDEZ\\certificados de depositos\\inactivos'

for nombre_archivo in os.listdir(carpeta):
    # Verificar si el archivo es un PDF con múltiples ".pdf"
    if nombre_archivo.endswith('.pdf'):
        # Obtener la ruta completa del archivo
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        
        # Eliminar múltiples ".pdf" y espacios antes de la extensión ".pdf"
        nombre_sin_extensiones = nombre_archivo.rstrip('.pdf').rstrip()
        nuevo_nombre = nombre_sin_extensiones + '.pdf'
        
        # Verificar si el nombre ha cambiado
        if nombre_archivo != nuevo_nombre:
            nueva_ruta_archivo = os.path.join(carpeta, nuevo_nombre)
            # Renombrar el archivo
            os.rename(ruta_archivo, nueva_ruta_archivo)
            print(f'Renombrado: "{nombre_archivo}" a "{nuevo_nombre}"')

print("Proceso completado.")

