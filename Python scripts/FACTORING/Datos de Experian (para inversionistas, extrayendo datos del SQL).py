# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 13:15:36 2024

@author: sanmiguel38
"""

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% EXCEL DETALLE DEUDORES para inversionistas
ubi_excel    = 'C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\DATOS PARA INVERSIONISTAS\\octubre 2024'
nombre_excel = 'DETALLE DEUDORES FINAL.xlsx'
filas_skip   = 1
sheet_nombre = 'Hoja 1'

#%%
os.chdir(ubi_excel)

excel_para_rellenar = pd.read_excel(io         = nombre_excel, 
                                    sheet_name = sheet_nombre,
                                    skiprows   = filas_skip,
                                    dtype      = str)


excel_para_rellenar['Ruc'] = excel_para_rellenar['Ruc'].str.strip()

excel = excel_para_rellenar[['Ruc', 'Razón social']]

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''

SELECT * FROM FACTORING..EXPERIAN_v2
WHERE FechaCorte = (SELECT MAX(FechaCorte) FROM FACTORING..EXPERIAN_v2)

'''
experian_data = pd.read_sql_query(query, conn)

del conn

#%% UNIENDO LOS DATOS CON LOS EXTRAIDOS DEL SQL
excel = excel.merge(experian_data[['N. DOCUMENTO', 'DEUDA SBS', 'CALIFICACIÓN', 'PROTESTO']],
                    left_on    = 'Ruc',
                    right_on   = 'N. DOCUMENTO',
                    how        = 'left')

#%% no hacen match (para que los incluyan a Experian)

no_match = excel[pd.isna(excel['N. DOCUMENTO'])]

if no_match.shape[0] > 0:
    print('casos que no hacen match:')
    print(no_match.shape[0])
    no_match[['Ruc', 'Razón social']].to_excel('agregar a Experian.xlsx')

#%%
excel.to_excel(f'datos.xlsx',
               index = False)



