# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:26:45 2025

@author: Joseph
"""

import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

#%%
f_corte = '12-2023'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SBS TXT\\BD-02\\prppgs (insumo)')

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
    SELECT
    	''                   AS 'CIS'   ,
    	NroPrestamo          AS 'CCR'   ,
    	numerocuota          AS 'NCUO'  ,
    	''                   AS 'MON'   ,
    	capitalPP2           AS 'MCUO'  ,
    	interesPP2           AS 'SIC'   ,
    	TotalCargoPP2        AS 'SCOM'  ,
    	''                   AS 'SEGS'  ,
    	''                   AS 'SIM'   ,
    	TotalPago            AS 'TCUO'  ,
    	FechaVencimiento     AS 'FVEP'  ,
    	''                   AS 'FCAN'  ,
    	DESCUENTOCAPITAL     AS 'SCONK' ,
    	DESCUENTOINTERES     AS 'SCONINT',
    	''                   AS 'DAKC'  ,   
    	''                   AS 'FOCAN' ,  
    	''                   AS 'SCA', 
        *  
    
    FROM ##ABC order by CodPrestamo, CodPrestamoCuota 
            '''

prppg_cuotas = pd.read_sql_query(query, conn, dtype = str)
conn.close()

print('nro de filas:')
print(prppg_cuotas.shape[0])
    
#%%
# Guardar en un archivo CSV
prppg_cuotas.to_csv(f"prppg {f_corte}.csv", 
                     index     = False, 
                     encoding  = "utf-8")

#%%
print('fin')

