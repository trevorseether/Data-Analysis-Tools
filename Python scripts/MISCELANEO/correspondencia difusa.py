# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:13:26 2024

@author: sanmiguel38
"""
#pip install fuzzywuzzy

import pandas as pd
from fuzzywuzzy import process

#%%

# Lista de nombres correctos de la base de datos
nombres_correctos = [
'ABOGADO',
'INGENIERO ELECTRONICO',
'INGENIERO CIVIL',
'INGENIERO DE SISTEMAS',
'ARQUITECTO',
'AUXILIAR DE ENFERMERIA',
'AUXILIAR DE CONTABILIDAD',
'MEDICO',
'BIBLIOTECOLOGA',
'BIOQUIMICA FARMACEUTICA',
'BOMBERO',
'CAJERO/A',
'CAMAROGRAFO/A',
'GANADERO',
'CHEF INTERNACIONAL',
'CHOFER',
'CINEMATOGRAFO/A',
'COCINERO/A',
'EMPLEADO',
'COMUNICADOR SOCIAL',

]

# Lista de nombres escritos manualmente
nombres_incorrectos = [
'ADMINISTRADOR',
'NO ESPECIFICADO',
'ABOGADO',
'CINEMATROGRAFO',
'AGENTE DE VIAJE',
'AGRIMENSOR Y TOPOGRAFO',
'AGRÓNOMO',
'ALBACEA',
'ALBAÑIL',

]

# Crear DataFrames
df_correctos   = pd.DataFrame(nombres_correctos,   columns=['nombre_correcto'])
df_incorrectos = pd.DataFrame(nombres_incorrectos, columns=['nombre_incorrecto'])

# Función para encontrar la mejor coincidencia
def find_best_match(name, choices):
    best_match = process.extractOne(name, choices)
    return best_match[0] if best_match[1] >= 70 else ''  # Usamos un umbral de 70% de similitud

# Aplicar la función de coincidencia difusa
df_incorrectos['nombre_correcto'] = df_incorrectos['nombre_incorrecto'].apply(lambda x: find_best_match(x, nombres_correctos))

# Mostrar los resultados
print(df_incorrectos)

import os
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\corrección de nombres')

df_incorrectos.to_excel('corregido parcialmente.xlsx')

