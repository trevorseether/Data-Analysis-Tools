# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 09:26:49 2023

@author: sanmiguel38
"""

import pandas as pd
import os
import numpy as np

#%%

os.chdir("C:\\Users\\sanmiguel38\\Desktop\\REPORTE ANABEL\\2023 JULIO\\25 JULIO 2023") #aqui se cambia la ubicación

df1=pd.read_excel("REPORTE 2023 BASES RENG-LD (4).xlsx",    # aqui se cambia el nombre del archivo si es necesario
                  dtype={'DNI': object})

#%%

'eliminando las filas que no tengan info en estas 3 columnas al mismo tiempo'

df1 = df1.dropna(subset=["NOMBRE SOCIO", "DNI", "PLANILLA"], how= 'all')
#%%

df1['FECHA DESEMBOLSO'] = pd.to_datetime(df1['FECHA DESEMBOLSO'], errors='coerce')

# Reemplazar los valores que no se pudieron convertir por np.nan
df1['FECHA DESEMBOLSO'] = df1['FECHA DESEMBOLSO'].replace({pd.NaT: np.nan})

#%%

'reemplazando los nulos por la fecha 1999/01/01'
df1['FECHA DESEMBOLSO'].fillna(value='1999-01-01', inplace=True)

'poniendo cero donde el monto desembolado es nulo'
df1['MONTO DESEMBOLSADO'].fillna(value=0, inplace=True)

#%%

'creando el excel donde estarán los datos'
try:
    ruta = "datos.xlsx"
    os.remove(ruta)
except FileNotFoundError:
    pass

df1.to_excel('datos.xlsx', index=False)


