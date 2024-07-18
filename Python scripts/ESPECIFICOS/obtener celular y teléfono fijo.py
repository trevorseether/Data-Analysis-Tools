# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 10:34:25 2024

@author: sanmiguel38
"""

import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\datos teléfonos')
#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'DOCUMENTO',

	sc.celular1 AS 'Celular', 
	SC.TelefonoFijo1


from socio as s 

LEFT JOIN sociocontacto as sc       ON sc.codsocio = s.codsocio

'''

df_fincore = pd.read_sql_query(query, conn,
                               dtype = {'codigosocio'   : str,
                                        'DOCUMENTO'     : str,
                                        'Celular'       : str,
                                        'TelefonoFijo1' : str})
df_fincore['Celular'] = df_fincore['Celular'].astype(str).str.replace('\.0', '', regex=True)

df_fincore['codigosocio'] = df_fincore['codigosocio'].str.strip()
df_fincore = df_fincore[~pd.isna(df_fincore['codigosocio'])]
df_fincore = df_fincore[(df_fincore['codigosocio'] != '')]
df_fincore = df_fincore[(df_fincore['codigosocio'] != 'None')]

duplicated = df_fincore[df_fincore.duplicated('codigosocio', keep=False)]

df_fincore.drop_duplicates(subset  = 'codigosocio',
                           inplace = True)

del conn

df_fincore['Socio']         = df_fincore['Socio'].str.strip()
df_fincore['DOCUMENTO']     = df_fincore['DOCUMENTO'].str.strip()
df_fincore['Celular']       = df_fincore['Celular'].str.strip()
df_fincore['TelefonoFijo1'] = df_fincore['TelefonoFijo1'].str.strip()

#%%
df_fincore.to_excel('datos total.xlsx',
                    index = False)

