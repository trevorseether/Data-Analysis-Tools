# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:00:07 2024

@author: sanmiguel38
"""

# =============================================================================
# dias de atraso según los meses
# =============================================================================

import pandas as pd
import pyodbc
import os
import warnings
warnings.filterwarnings('ignore')

#%%
fecha_corte = '2024-03-31'

'Directorio de trabajo:'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\dias de atraso, 12 meses a partir del desembolso')

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''
SELECT  
	FechaCorte1,
	FechadeDesembolso21,
	EOMONTH(FechadeDesembolso21) as 'ULT DÍA DESEMBOLSO',
	DATEDIFF(MONTH, EOMONTH(FechadeDesembolso21), FechaCorte1) as 'MESES DIFERENCIA',
	ApellidosyNombresRazonSocial2,
	NumerodeDocumento10,
	TipodeDocumento9,
	Nro_Fincore,
	DiasdeMora33,
	TipodeProducto43,
		CASE
			WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
			WHEN TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29) THEN 'MYPE'
			END AS 'PRODUCTO TXT'
FROM anexos_riesgos3..ANX06
WHERE FechaCorte1 >= '20210101'
AND TipodeProducto43 in (34,35,36,37,38,39,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29)
ORDER BY FechaCorte1, ApellidosyNombresRazonSocial2

'''
base = pd.read_sql_query(query, conn)

del conn

#%%
corte_actual = base[base['FechaCorte1'] == pd.Timestamp(fecha_corte)]
corte_actual.rename(columns = {"DiasdeMora33" : "Dias de mora actual"}, 
                    inplace = True)

owo = corte_actual.copy()

#%% merges
for i in range(1,13):
    owo = owo.merge(base[base['MESES DIFERENCIA'] == i][['Nro_Fincore', "DiasdeMora33"]],
                             on  = 'Nro_Fincore',
                             how = 'left')

owo.columns = ['FechaCorte1',          'FechadeDesembolso21', 'ULT DÍA DESEMBOLSO',
               'MESES DIFERENCIA',     'ApellidosyNombresRazonSocial2',
               'NumerodeDocumento10',  'TipodeDocumento9',    'Nro_Fincore',
               'Dias de mora actual',  'TipodeProducto43',    'PRODUCTO TXT',
               'Días de atraso 1er mes', 
               'Días de atraso 2do mes',
               'Días de atraso 3er mes',
               'Días de atraso 4to mes',
               'Días de atraso 5to mes',
               'Días de atraso 6to mes',
               'Días de atraso 7mo mes',
               'Días de atraso 8vo mes',
               'Días de atraso 9no mes',
               'Días de atraso 10mo mes',
               'Días de atraso 11vo mes',
               'Días de atraso 12vo mes']

owo.drop_duplicates(subset  = 'Nro_Fincore', 
                    inplace = True)

#%% A EXCEL
owo.to_excel('dias de atraso.xlsx',
             index = False)

