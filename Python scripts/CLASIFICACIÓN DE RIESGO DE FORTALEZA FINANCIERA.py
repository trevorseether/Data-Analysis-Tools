# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 19:17:42 2024

@author: sanmiguel38
"""

import pandas as pd
import pyodbc
import os

import warnings
warnings.filterwarnings('ignore')

#%%
mes = '20230228'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\clasificación de riesgo, fortaleza financiera')

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
querrrry = f'''
select
	Nro_Fincore, 
	ApellidosyNombresRazonSocial2,
	TipodeCredito19,
	case 
when TipodeCredito19='06' then 'Crédito Corporativo'
when TipodeCredito19='07' then 'Grande Empresa'
when TipodeCredito19='08' then 'Mediana Empresa'
when TipodeCredito19='09' then 'Pequeña Empresa'
when TipodeCredito19='10' then 'Micro Empresa'
when TipodeCredito19='11' then 'Consumo Revolvente'
when TipodeCredito19='12' then 'Consumo No Revolvente'
when TipodeCredito19='13' then 'Hipotecario'
when TipodeCredito19='20' then 'COOPAC'
end TxtTipoCredito,

	Monedadelcredito17,
	CASE
		WHEN Monedadelcredito17 = 2 THEN 'Dolares'
		WHEN Monedadelcredito17 = 1 THEN 'Soles'
		end as 'moneda txt',

	Saldodecolocacionescreditosdirectos24,
	SaldodeGarantiasAutoliquidables35,
	SaldosdeGarantiasPreferidas34,
	TasadeInteresAnual23,
	DiasdeMora33
from anexos_riesgos3..ANX06
where FechaCorte1 = '{mes}'
ORDER BY Saldodecolocacionescreditosdirectos24 DESC

'''
base = pd.read_sql_query(querrrry, conn)

del conn
#%%%
total_saldo = base.pivot_table(values  = 'Saldodecolocacionescreditosdirectos24',
                               index   = 'ApellidosyNombresRazonSocial2',
                               aggfunc = 'sum').reset_index()

df_ordenado = total_saldo.sort_values(by = 'Saldodecolocacionescreditosdirectos24', ascending = False)
df_ordenado['Saldodecolocacionescreditosdirectos24'] = df_ordenado['Saldodecolocacionescreditosdirectos24'].round(2)
top_20 = df_ordenado.head(20)

#%% tipo de crédito

base = base.sort_values(by = 'Saldodecolocacionescreditosdirectos24', ascending = False)
tipo_credito = base.drop_duplicates(subset= 'ApellidosyNombresRazonSocial2').head(50)[['ApellidosyNombresRazonSocial2',
                                                                                       'TxtTipoCredito']]

#%% tipo de moneda

base = base.sort_values(by = 'Saldodecolocacionescreditosdirectos24', ascending = False)
tipo_moneda = base.drop_duplicates(subset= 'ApellidosyNombresRazonSocial2').head(50)[['ApellidosyNombresRazonSocial2',
                                                                                       'moneda txt']]

#%% tasa anual

base = base.sort_values(by = 'Saldodecolocacionescreditosdirectos24', ascending = False)
tasa_anual = base.drop_duplicates(subset= 'ApellidosyNombresRazonSocial2').head(50)[['ApellidosyNombresRazonSocial2',
                                                                                       'TasadeInteresAnual23']]

#%% dias de atraso

base = base.sort_values(by = 'Saldodecolocacionescreditosdirectos24', ascending = False)
dias_mora = base.drop_duplicates(subset= 'ApellidosyNombresRazonSocial2').head(50)[['ApellidosyNombresRazonSocial2',
                                                                                    'DiasdeMora33']]

#%% número de créditos
nro_cred = base.pivot_table(values = 'Nro_Fincore',
                            index  = 'ApellidosyNombresRazonSocial2',
                            aggfunc= 'count').reset_index()

nro_cred.rename(columns = {'Nro_Fincore' : 'Nro créditos'}, inplace = True)

#%% GARANTÍAS
base['Garantias Preferidas'] = base['SaldodeGarantiasAutoliquidables35'] + base['SaldosdeGarantiasPreferidas34']
garantias = base.pivot_table(values = 'Garantias Preferidas',
                             index  = 'ApellidosyNombresRazonSocial2',
                             aggfunc= 'sum').reset_index() 

#%% los left joins
top_20['Sector Economico'] = ''
# top_20['Garantias Preferidas'] = ''
top_20['Garantias No Preferidas'] = 0

top_20 = top_20.merge(tipo_credito,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

top_20 = top_20.merge(tipo_moneda,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

top_20 = top_20.merge(tasa_anual,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

top_20 = top_20.merge(dias_mora,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

top_20 = top_20.merge(nro_cred,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

top_20 = top_20.merge(garantias,
                      on = 'ApellidosyNombresRazonSocial2',
                      how = 'left')

#%%
top_20 = top_20[['ApellidosyNombresRazonSocial2',
                 'TxtTipoCredito',
                 'Sector Economico',
                 'moneda txt', 
                 'TasadeInteresAnual23',
                 'Garantias Preferidas', 
                 'Garantias No Preferidas',
                 'DiasdeMora33',
                 'Saldodecolocacionescreditosdirectos24']]

#%%
top_20.to_excel(f'top20 {mes}.xlsx')

# %%
# =============================================================================
#                               REPROGRAMADOS
# =============================================================================
import pandas as pd

repro_archivo = 'Rpt_DeudoresSBS Anexo06 - Creditos Reprogramados ENERO-2022 - No incl castigados.xlsx'

repro_ubi     = 'C:\\Users\\sanmiguel38\\Desktop\\Alexander\\Entregas Areas\\Reporte Sbs\\Reportes que envia Cesar'

CORTE         = 20220131

filas_skip    = 3
#%%
repro = pd.read_excel(repro_ubi + '\\' + repro_archivo,
                      skiprows = filas_skip,
                      dtype =  {'Código Socio 7/'        : str,
                                'Nro Prestamo \nFincore' : str,
                                'Tipo de Crédito 19/'    : str}
                      )

#%%
def tipo_cred_txt(df):
    if df['Tipo de Crédito 19/'] == '06':
        return 'Crédito Corporativo'
    if df['Tipo de Crédito 19/'] == '07':
        return 'Grande Empresa'
    if df['Tipo de Crédito 19/'] == '08':
        return 'Mediana Empresa'
    if df['Tipo de Crédito 19/'] == '09':
        return 'Pequeña Empresa'
    if df['Tipo de Crédito 19/'] == '10':
        return 'Micro Empresa'
    if df['Tipo de Crédito 19/'] == '11':
        return 'Consumo Revolvente'
    if df['Tipo de Crédito 19/'] == '12':
        return 'Consumo No Revolvente'
    if df['Tipo de Crédito 19/'] == '13':
        return 'Hipotecario'
    # if df['Tipo de Crédito 19/'] == '20':
    #     return 'COOPAC'
    else:
        return ''
repro['TipoCredTXT'] = repro.apply(tipo_cred_txt, axis = 1)

print('Debe salir cero:')
print(repro[repro['TipoCredTXT'] == ''].shape[0])

#%% como es a nivel de socio, filtramos y nos quedamos con el que tenga mayor saldo
repro = repro.sort_values(by = 'Saldo de colocaciones (créditos directos) 24/', ascending = False)
repro_sin_duplicados = repro.drop_duplicates(subset= 'Código Socio 7/', keep = 'first')

#%% pivots
nro_repro = repro_sin_duplicados.pivot_table(values  = 'Tipo de Crédito 19/',
                                             columns = 'TipoCredTXT',
                                             aggfunc = 'count')

nro_repro['fecha_corte'] = CORTE

#%%
cols = [
        'corporativo', 
        'grande empresa',
        'Mediana Empresa', 
        'Pequeña Empresa',
        'Micro Empresa',
        'Consumo No Revolvente',
        'Hipotecario',
        'fecha_corte'
        ]

df_vacio = pd.DataFrame(columns = cols)

df_num_repros = pd.concat([df_vacio, nro_repro], ignore_index = True)
df_num_repros = df_num_repros.fillna(0)

#%% pivot por saldo de cartera
saldo_repro = repro.pivot_table(values  = 'Saldo de colocaciones (créditos directos) 24/',
                                columns = 'TipoCredTXT',
                                aggfunc = 'sum')
saldo_repro['fecha_corte'] = CORTE

df_vacio = pd.DataFrame(columns = cols)

df_saldo_repros = pd.concat([df_vacio, saldo_repro], ignore_index = True)
df_saldo_repros = df_saldo_repros.fillna(0)

print(repro['Saldo de colocaciones (créditos directos) 24/'].sum())


