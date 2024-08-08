# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 17:17:55 2024

@author: sanmiguel38
"""

# =============================================================================
# Req Sunat - Tabla N 001
# =============================================================================

import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\pedidos\\contabilidad\\requerimiento sunat\\TABLA N 001')

excel_enviado_por_contabilidad = 'tabla 001 SUNAT2024 I.xlsx'

skip_filas = 0

#%%
columna_nro_identificador_del_socio = 'DOC_IDENTIDAD  ' #columna con el dni del socio

df_para_completar = pd.read_excel(io       = excel_enviado_por_contabilidad, 
                                  skiprows = skip_filas,
                                  dtype    = {columna_nro_identificador_del_socio  : str,
                                              'CodSoc'                             : str})

df_para_completar[columna_nro_identificador_del_socio] = df_para_completar[columna_nro_identificador_del_socio].str.strip()

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT 	
	iif(A.CodTipoPersona =1, A.nroDocIdentidad, A.nroruc) AS 'Doc_Identidad',
	A.ApellidoPaterno,
	A.ApellidoMaterno,
	A.Nombres,
	A.razonsocial,
--B.FechaObservacion,
A.FechaInscripcion,
A.FechaNacimiento,
	CASE
		WHEN B.CodValorNuevo = 301 THEN 'INHABIL'
        WHEN B.CodValorNuevo = 532 THEN 'INHABIL-FALLECIDO'
	ELSE ' '
	END AS 'OBSERVACIÓN',

	CASE
		WHEN B.CodValorNuevo IN (301,532) THEN B.FechaObservacion
	ELSE ''
	END AS	'fecha_egreso'
    
FROM 
	Socio AS A
LEFT JOIN 
	SocioObservacion AS B ON A.CODSOCIO = B.CODSOCIO

--WHERE 
--	B.CodValorNuevo IN (301,532)

ORDER BY iif(A.CodTipoPersona =1, A.nroDocIdentidad, A.nroruc)

'''

df_fincore = pd.read_sql_query(query, 
                               conn, 
                               dtype = {'Doc_Identidad' : str})

df_fincore['Doc_Identidad'] = df_fincore['Doc_Identidad'].str.strip()

df_fincore = df_fincore.sort_values(by = 'OBSERVACIÓN', ascending = False)
df_fincore = df_fincore.drop_duplicates(subset = 'Doc_Identidad', keep='first')

df_fincore['fecha_egreso'] = df_fincore['fecha_egreso'].replace(pd.Timestamp('1900-01-01 00:00:00') , '')

#%% MERGE
df_completado = df_para_completar[[columna_nro_identificador_del_socio,
                                   'Apellidos y Nombres']].merge(df_fincore[['Doc_Identidad'  ,
                                                                             'ApellidoPaterno',
                                                                             'ApellidoMaterno',
                                                                             'Nombres'        ,
                                                                             'razonsocial'    ,
                                                                             'fecha_egreso', 'OBSERVACIÓN']],
                                                                 left_on  = columna_nro_identificador_del_socio,
                                                                 right_on = 'Doc_Identidad',
                                                                 how      = 'left')
# comprobación merge
sin_match = df_completado[pd.isna(df_completado['Doc_Identidad'])]
if sin_match.shape[0] > 0:
    print('algunos no hicieron bien el match, investigar')
    print(sin_match)
else:
    pass

#%% creación excel
df_completado.to_excel('Tabla N 001 SUNAT.xlsx',
                       index = False)
