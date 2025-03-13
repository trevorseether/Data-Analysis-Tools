# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 10:09:06 2025

@author: sanmiguel38
"""

# =============================================================================
#                                BD - 04
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SBS TXT\\BD-03-B') # no cambiar

garantias_preferidas_total = pd.read_excel('Anexo 05 - Informe de Clasificación de Deudores y Proviciones_vh.xlsx',
                                           skiprows   = 4,
                                           dtype      = str,
                                           sheet_name = 'Base Final') # no cambiar

fecha_corte = '20230331' # formato de SQL

#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
        SELECT
        
        	PartidaRegistral8  AS 'CODGR',
        	CodigoSocio7       AS 'CIS',
        	Nro_Fincore        AS 'CCR',
        	0                  AS 'MGU',
        	'4'                AS 'CGR'
        
        FROM anexos_riesgos3..ANX06
        WHERE FechaCorte1 = '{fecha_corte}'
        AND SaldosdeGarantiasPreferidas34 > 0
'''
ga_pref_anx06 = pd.read_sql_query(query, conn)

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

año = int(fecha_corte[0:4])
mes = int(fecha_corte[4:6])

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = f'''
    
    SELECT
    	* 
    FROM 
    	TipoCambioSBS
    WHERE 
    	Anno = {año}
    AND
    	Mes = {mes}

'''

df_tc_sbs = pd.read_sql_query(query, conn)

tipo_cambio = df_tc_sbs['TCSBS'][0]

#%%
monto_garant = garantias_preferidas_total[['Código / Número de la\ngarantía',
                                           'Moneda de la garantía',
                                           'Valor de constitución de la garantía\n(gravamen)']]

monto_garant.columns = ['nro finc', 'mon', 'valor']
monto_garant['valor'] = monto_garant['valor'].astype(float)

monto_garant["nro finc"] = monto_garant["nro finc"].str.replace("01-", "", regex=False)

def monto_mn(df):
    if df['mon'] == '2':
        return df['valor'] * tipo_cambio
    else:
        return df['valor']
monto_garant["valor MN"] = monto_garant.apply(monto_mn, axis = 1)
monto_garant["valor MN"] = monto_garant["valor MN"].round(2)

#%%
ga_pref_anx06 = ga_pref_anx06.merge(monto_garant[['nro finc', "valor MN"]],
                                    left_on  = 'CCR',
                                    right_on = 'nro finc',
                                    how      = 'left')

alerta = ga_pref_anx06[ pd.isna(ga_pref_anx06["valor MN"]) ]
if alerta.shape[0] > 0:
    print('alerta, error en el match')

ga_pref_anx06['MGU'] = ga_pref_anx06['valor MN']

del ga_pref_anx06['nro finc']
del ga_pref_anx06["valor MN"]

#%%
nombre = '20523941047_BD02B_' + fecha_corte[0:6] + '.txt'

ga_pref_anx06.to_csv(nombre, 
                     sep      = '\t', 
                     index    = False, 
                     encoding = 'utf-8')

