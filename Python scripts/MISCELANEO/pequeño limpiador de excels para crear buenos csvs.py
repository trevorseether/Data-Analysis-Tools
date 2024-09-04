# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 16:01:34 2024

@author: sanmiguel38
"""
import pandas as pd
import os 

#%%
os.chdir('R:\\REPORTES DE GESTIÓN\\DESARROLLO\\Implementacion NetBank\\Datos para Migracion\\Crediticio\\Envio 05 - 26Ago24')
excel = 'Axon26082024.xlsx'

sheet_nombre = 'prgar'
#%%
######################################################################
df1 = pd.read_excel(io         = excel,
                    skiprows   = 2,
                    sheet_name = sheet_nombre,
                    dtype      = str)
print(df1.shape[1])

# df1['CodigoSocio'] = df1['CodigoSocio'].str.strip()
# df1 = df1.replace('Ü', 'U', regex = True )
# df1 = df1.replace('Á', 'A', regex = True )
# df1 = df1.replace('É', 'E', regex = True )
# df1 = df1.replace('Í', 'I', regex = True )
# df1 = df1.replace('Ó', 'O', regex = True )
# df1 = df1.replace('Ú', 'U', regex = True )

df1 = df1.replace(';', '', regex = True)

df1 = df1.fillna('')

#%%
df1.to_csv(sheet_nombre + '.csv', 
           index    =  False,
           encoding =  'utf-8-sig', #'utf-8',
           header   =  False,
           sep      =  ';')

