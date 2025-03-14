# -*- coding: utf-8 -*-
"""
Created on Fri May 31 16:49:43 2024

@author: sanmiguel38
"""

# =============================================================================
# ESTRUCTURA PARA REASIGNACIÓN DE FUNCIONARIO
# =============================================================================
import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\MIGRACIÓN DE CARTERA\\aplicar en febrero 2025')

nombre = 'migra.xlsx'

corte       = 'FEBRERO 2025'
nro_fincore = 'NRO FINCORE'     #columna del fincore del excel
nuevo_func  = 'FN'              #columna del nuevo funcionario del excel
pestaña     = 'Migracion'       #pestaña del excel
filas_skip  = 0

#%%
reasignacion = pd.read_excel(io         = nombre, 
                             sheet_name = pestaña,
                             skiprows   = filas_skip)

#%%

reasignacion = reasignacion[[nro_fincore, nuevo_func]]

reasignacion['Fincore_format'] = reasignacion[nro_fincore].astype(int).astype(str).str.zfill(8)

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT
		--------------------------------------------------------------
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	CASE 
		WHEN p.CodPrestamoFox IS NOT NULL THEN
		RIGHT(CONCAT('000000',p.CodPrestamoFox),6)
	ELSE RIGHT(CONCAT('0000000',p.numero),8)
		END as 'pagare_fox', 
		--------------------------------------------------------------
	pro.CodGrupoCab,
	pro.descripcion as 'Funcionario',
	FI.CODIGO AS 'COD_FINALIDAD'

FROM prestamo AS p
INNER JOIN socio AS s             ON s.codsocio = p.codsocio
INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'

AND s.codigosocio     > 0
'''

df_codgrupocab = pd.read_sql_query(query, conn)

df_codgrupocab.drop_duplicates(subset  = 'pagare_fincore', 
                               inplace = True)

del conn

#%% LEFT JOIN
reasignacion = reasignacion.merge(df_codgrupocab[['pagare_fincore', 'CodGrupoCab', 'Funcionario']],
                                  left_on  = 'Fincore_format',
                                  right_on = 'pagare_fincore',
                                  how      = 'left')

reasignacion.drop_duplicates(subset  = 'Fincore_format', 
                             inplace = True)

#%%
para_excel = reasignacion[['pagare_fincore',
                           'Funcionario',
                           'CodGrupoCab',
                           nuevo_func
                           ]]

para_excel['CodGrupoCab (nuevo administrador)'] = ''

para_excel.columns = ['FINCORE',
                      'ADMINISTRADOR ACTUAL',
                      'CodGrupoCab (administrador actual)',
                      'REASIGNACIÓN',
                      'CodGrupoCab (nuevo administrador)',
                      ]

#%%
codgrupocab = df_codgrupocab[['CodGrupoCab', 'Funcionario']].drop_duplicates(subset='CodGrupoCab')
codgrupocab['CodGrupoCab'] = codgrupocab['CodGrupoCab'].astype(int).astype(str)
codgrupocab = codgrupocab.drop_duplicates(subset = 'Funcionario')

filas_original = para_excel.shape[0]

para_excel = para_excel.merge(codgrupocab,
                              left_on  = 'REASIGNACIÓN',
                              right_on = 'Funcionario',
                              how = 'left' )

filas_nuevo = para_excel.shape[0]
if filas_nuevo != filas_original:
    print('alerta alerta, se han duplicado con este merge')

para_excel['CodGrupoCab (nuevo administrador)'] = para_excel['CodGrupoCab']

del para_excel['CodGrupoCab']
del para_excel['Funcionario']

#%%
para_excel.to_excel(f'Traslado {pestaña} Estructurado {corte}.xlsx',
                    index = False)

#%% QUERY PARA AÑADIR LAS REASIGNACIONES MANUALMENTE
print('''
SELECT 
	* 
FROM 
	grupocab
WHERE 
	descripcion LIKE '%David%'
''')

