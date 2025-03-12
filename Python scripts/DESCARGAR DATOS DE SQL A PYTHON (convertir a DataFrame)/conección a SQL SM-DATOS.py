# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:21:23 2023

@author: Joseph Montoya
"""

'''
###############################################################################
 CONECCIÓN A SQL SERVER SM-DATOS
###############################################################################
'''
#MÓDULOS NECESARIOS:
import pandas as pd
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''
SELECT
	FechaCorte1,
	Nro_Fincore, 
	ApellidosyNombresRazonSocial2,
	MontodeDesembolso22,
	FechadeDesembolso21,
	Saldodecolocacionescreditosdirectos24,
	CapitalVencido29,
	CapitalenCobranzaJudicial30,
	SaldosdeCreditosCastigados38,
	ProvisionesConstituidas37,
	ProvisionesRequeridas36,
	originador, administrador,
	PLANILLA, NUEVA_PLANILLA,
	TipodeProducto43,
	CASE
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (20,21,22,23,24,25,29) THEN 'MICRO EMPRESA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIA'
		END AS 'PRODUCTO TXT'
FROM
	anexos_riesgos3..anx06
WHERE 
	FechaCorte1 = '20230831'

'''
base = pd.read_sql_query(query, conn)

conn.close()

#%%
print(base)

#%%



