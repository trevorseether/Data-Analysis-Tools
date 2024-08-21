# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 16:01:34 2024

@author: sanmiguel38
"""
import pandas as pd
import os 

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\AXON ENVÍO limpieza de datos\\limpieza 1\\axon csvs')
excel = 'AXON_ENVIO_II.xlsx'

sheet_nombre = 'prppg (2)'
######################################################################
df1 = pd.read_excel(io         = excel,
                    skiprows   = 3,
                    sheet_name = sheet_nombre,
                    dtype      = str)

# df1['CodigoSocio'] = df1['CodigoSocio'].str.strip()
df1 = df1.replace('Ü', 'U', regex=True)
df1 = df1.replace('Á', 'A', regex=True)
df1 = df1.replace('É', 'E', regex=True)
df1 = df1.replace('Í', 'I', regex=True)
df1 = df1.replace('Ó', 'O', regex=True)
df1 = df1.replace('Ú', 'U', regex=True)
df1 = df1.replace(';', '', regex=True)

df1 = df1.fillna('')

df1.to_csv(sheet_nombre + 'nuevo.csv', 
           index    =  False,
           encoding =  'utf-8', #'utf-8',
           header   =  False,
           sep      =  ';')

