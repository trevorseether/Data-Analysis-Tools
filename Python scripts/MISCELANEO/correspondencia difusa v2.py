# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:50:28 2024

@author: sanmiguel38
"""

import pandas as pd
from fuzzywuzzy import process
import os
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\corrección de nombres')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\total créditos')

excel_correctos = 'data de DNI.xlsx'
sheet_correctos = 'para búsqueda'

excel_incorrectos = 'data de DNI.xlsx'
sheet_incorrectos = 'Hoja5'

#%%
# Crear DataFrames
df_correctos   = pd.read_excel(io        = excel_correctos,
                              sheet_name = sheet_correctos
                              )

df_incorrectos = pd.read_excel(io         = excel_incorrectos,
                               sheet_name = sheet_incorrectos
                              )

#%% columnas

columna_df_incorrecto = df_incorrectos['NombSocios']
nombres_correctos     = list(df_correctos['asd'])

#%%
# Función para encontrar la mejor coincidencia
def find_best_match(name, choices):
    best_match = process.extractOne(name, choices)
    return best_match[0] if best_match[1] >= 90 else ''  # Umbral de similitud

# Aplicar la función de coincidencia difusa
df_incorrectos['nombre_correcto'] = columna_df_incorrecto.apply(lambda x: find_best_match(x, nombres_correctos))

# Mostrar los resultados
print(df_incorrectos)

df_incorrectos.to_excel('corregido parcialmente.xlsx')

