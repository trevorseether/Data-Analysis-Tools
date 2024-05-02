# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 10:51:10 2023

@author: sanmiguel38
"""

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
import pandas as pd
import pyodbc

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

base = pd.read_sql_query('''
SELECT
	FechaCorte1, year(FechaCorte1) as 'year', month(FechaCorte1) as 'month',
	Nro_Fincore, 
	ApellidosyNombresRazonSocial2,
	MontodeDesembolso22,
	FechadeDesembolso21,
	Saldodecolocacionescreditosdirectos24,
	CapitalVencido29,
	CapitalenCobranzaJudicial30, CapitalVencido29 + CapitalenCobranzaJudicial30 as 'deteriorado',
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
	FechaCorte1 > 0
''', conn)

del conn

#%%

# Definir una función personalizada para calcular la morosidad

# Crear la tabla pivote utilizando la función personalizada
tabla_pivot_vencido = base.pivot_table(columns = "year",
                               values  = ['deteriorado'],
                               index   = ["month"],
                               margins = False,
                               aggfunc = 'sum')


# Draw a heatmap with the numeric values in each cell
f, ax = plt.subplots(figsize=(9, 6))

# Configura el formato 'f' en lugar de 'd' para números de punto flotante
sns.heatmap(tabla_pivot_vencido, 
            annot=True, 
            fmt=".0f", 
            linewidths=.5, 
            ax=ax)

#%%

tabla_pivot_saldo = base.pivot_table(columns = "year",
                               values        = ['Saldodecolocacionescreditosdirectos24'],
                               index         = ["month"],
                               margins       = False,
                               aggfunc       = 'sum')


# Draw a heatmap with the numeric values in each cell
f, ax = plt.subplots(figsize=(9, 6))

# Configura el formato 'f' en lugar de 'd' para números de punto flotante
sns.heatmap(tabla_pivot_saldo, 
            annot=True, 
            fmt=".0f", 
            linewidths=.5, 
            ax=ax)

#%% p_morosidad
p_morosidad = tabla_pivot_vencido['deteriorado'] / tabla_pivot_saldo['Saldodecolocacionescreditosdirectos24']

# Draw a heatmap with the numeric values in each cell
f, ax = plt.subplots(figsize=(9, 6))
# Configura el formato 'f' en lugar de 'd' para números de punto flotante
sns.heatmap(p_morosidad, 
            annot=True, 
            fmt=".4f", 
            linewidths=.5, 
            ax=ax)

