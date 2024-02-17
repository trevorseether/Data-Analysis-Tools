# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 19:17:42 2024

@author: sanmiguel38
"""

import pandas as pd
import pyodbc
#%%
mes = '20231130'

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

#%% los left joins
top_20['Sector Economico'] = ''
top_20['Garantias Preferidas'] = ''
top_20['Garantias No Preferidas'] = 0
top_20['Garantias Preferidas'] = ''

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

