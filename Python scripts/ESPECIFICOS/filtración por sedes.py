# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 13:46:14 2023

@author: sanmiguel38
"""

import pyodbc
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import os
#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%
# =============================================================================
# leyendo creditos cancelados cuyo desembolso haya sido posterior al 2022
# =============================================================================
server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

########################################################
###                CAMBIAR LA FECHA               ######
########################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
query = '''

select 	
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	TMD.Descripcion
FROM prestamo as p
LEFT JOIN SolicitudCredito AS SOLCRED
ON (P.CodSolicitudCredito = SOLCRED.CodSolicitudCredito) --numero --CodSolicitudCredito
left join TablaMaestraDet AS TMD
ON TMD.codtabladet = SOLCRED.CanalAfiliacion
where TMD.CodTablaCab = 140
'''

df_canal = pd.read_sql_query(query, conn)
del conn

df_canal['Descripcion'].unique()

canal_trujillo = df_canal[df_canal['Descripcion'] == 'CANAL OFICINA TRUJILLO']

canal_arequipa = df_canal[df_canal['Descripcion'] == 'CANAL OFICINA AREQUIPA']

canal_canete   = df_canal[df_canal['Descripcion'] == 'CANAL OFICINA CAÑETE']

canal_tarapoto = df_canal[df_canal['Descripcion'] == 'CANAL OFICINA TARAPOTO']

#%%
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 SETIEMBRE\\FINAL'
nom = 'Rpt_DeudoresSBS Anexo06 - Setiembre 2023 - campos ampliados v04.xlsx'

df_set = pd.read_excel(ubi + '\\' + nom,
                       skiprows = 2,
                       dtype = {'Nro Prestamo \nFincore' : str})

anx_trujillo = df_set[(df_set['Nro Prestamo \nFincore'].isin(list(canal_trujillo['pagare_fincore']))) |
                      (df_set['Funcionaria TXT'].isin(['JESSICA PISCOYA VIDARTE',
                                                       'JOSE SANCHEZ FLORES',
                                                       'MILTON MERLYN JUAREZ HORNA',
                                                       'PAULO SARE',
                                                       'ROY NARVAEZ',
                                                       'PROSEVA TRUJILLO']))]

anx_arequipa = df_set[(df_set['Nro Prestamo \nFincore'].isin(list(canal_arequipa['pagare_fincore']))) |
                      (df_set['Funcionaria TXT'].isin(['ADOLFO HUAMAN',
                                                       'CESAR MEDINA DIAZ',
                                                       'HAROLD RAMOS HINOJOSA', ############################################################
                                                       'RILDO URRUTIA PANCORVO', ##################################
                                                       'PAMELA GARCIA', ################################
                                                       'DAYANA CHIRA',
                                                       'ESTHER RAMIREZ RODRIGUEZ',
                                                       'JESSICA SOLORZANO LLACMA',
                                                       'MARIA CRISTINA MARTINEZ PAZ',
                                                       'MARIBEL PUCHO CALA',
                                                       'PROSEVA AREQUIPA']))]

anx_canete   = df_set[(df_set['Nro Prestamo \nFincore'].isin(list(canal_canete['pagare_fincore']))) |
                      (df_set['Funcionaria TXT'].isin(['PROSEVA CAÑETE']))]

anx_tarapoto = df_set[(df_set['Nro Prestamo \nFincore'].isin(list(canal_tarapoto['pagare_fincore']))) |
                      (df_set['Funcionaria TXT'].isin(['CESAR MERA CASA',
                                                       'WILLIAMS TRAUCO PAREDES',
                                                       'PROSEVA TARAPOTO']))]


lista = list(anx_trujillo['Nro Prestamo \nFincore']) + \
        list(anx_arequipa['Nro Prestamo \nFincore']) + \
        list(anx_canete['Nro Prestamo \nFincore']) + \
        list(anx_tarapoto['Nro Prestamo \nFincore'])

set_de_la_lista = set(lista)
print(len(lista))
print(len(set_de_la_lista))
print('si sale igual todo bien')

#%% excel 
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\solicitud de wilfredo')

anx_trujillo[['Funcionaria TXT', 'Nro Prestamo \nFincore']].to_excel('fincore trujillo.xlsx')
anx_arequipa[['Funcionaria TXT', 'Nro Prestamo \nFincore']].to_excel('fincore arequipa.xlsx')
anx_canete[['Funcionaria TXT', 'Nro Prestamo \nFincore']].to_excel('fincore canete.xlsx')
anx_tarapoto[['Funcionaria TXT', 'Nro Prestamo \nFincore']].to_excel('fincore tarapoto.xlsx')

