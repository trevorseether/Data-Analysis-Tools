# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 12:24:36 2023

@author: sanmiguel38
"""

###########################################################
############# VERIFICACIONES DEL ANEXO06 ##################
###########################################################

import pandas as pd
import os
import pyodbc
import numpy as np

#%%
#VAMOS A IMPORTAR EL ANEXO06 DEL MES PASADO
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
df_mes_pasado = pd.read_sql_query('''
                            
declare @fecha as datetime
set @fecha = '20230531'  -- aqui se pone el mes pasado

select 
Nro_Fincore, ApellidosyNombresRazonSocial2, FechadeNacimiento3,
NumerodeDocumento10, DiasdeMora33, ClasificaciondelDeudorconAlineamiento15
from anexos_riesgos2..Anx06_preliminar
where FechaCorte1 = @fecha

order by ApellidosyNombresRazonSocial2
                            
                            ''', conn)

del conn

df_mes_pasado['ApellidosyNombresRazonSocial2'] = df_mes_pasado['ApellidosyNombresRazonSocial2'].str.strip()
df_mes_pasado['NumerodeDocumento10'] = df_mes_pasado['NumerodeDocumento10'].str.strip()

df_mes_pasado = df_mes_pasado.rename(columns={'ApellidosyNombresRazonSocial2': 'nombres y apellidos mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'FechadeNacimiento3': 'FechaNacimiento mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'NumerodeDocumento10': 'Documento mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'DiasdeMora33': 'DíasMora mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'ClasificaciondelDeudorconAlineamiento15': 'Clasificación Alineamiento mes pasado'})

#%%
#leemos el anexo ampliado de este mes
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 JUNIO\\parte 2')
df = pd.read_excel('Rpt_DeudoresSBS_Junio 2023 HT version 03.xlsx',
                 dtype={'Registro 1/': object, 
                        'Fecha de Nacimiento 3/': object,
                        'Código Socio 7/':object, 
                        'Número de Documento 10/': object,
                        'Relación Laboral con la Cooperativa 13/':object, 
                        'Código de Agencia 16/': object,
                        'Moneda del crédito 17/':object, 
                        'Numero de Crédito 18/': object,
                        'Tipo de Crédito 19/': object,
                        'Sub Tipo de Crédito 20/': object,
                        'Fecha de Desembolso 21/': object,
                        'Cuenta Contable 25/': object,
                        'Tipo de Producto 43/': object,
                        'Fecha de Vencimiento Origuinal del Credito 48/': object,
                        'Fecha de Vencimiento Actual del Crédito 49/': object,
                        '''Nro Prestamo 
Fincore''': object},
                     skiprows=2
                     )
df['Apellidos y Nombres / Razón Social 2/'] = df['Apellidos y Nombres / Razón Social 2/'].str.strip()
df['Número de Documento 10/'] = df['Número de Documento 10/'].str.strip()

df = df.rename(columns={'Apellidos y Nombres / Razón Social 2/': 'nombres y apellidos mes actual'})


#%%
#nos quedamos solo con las columnas necesarias
anx = df[['nombres y apellidos mes actual',
          'Fecha de Nacimiento 3/',
          'Número de Documento 10/',
          'Dias de Mora 33/',
          'Clasificación del Deudor con Alineamiento 15/',
          '''Nro Prestamo 
Fincore'''
          ]]

anx = anx.rename(columns={'''Nro Prestamo 
Fincore''': "fincore"})

del df

#%%
#filtramos el dataframe actual para que solo 
#tenga los números fincore que aparecen el
#mes pasado

df_filtrado = anx[anx['fincore'].isin(df_mes_pasado['Nro_Fincore'])]

#%%
#unimos

union = df_filtrado.merge(df_mes_pasado, 
                          how='left', 
                          left_on=['fincore'], 
                          right_on=['Nro_Fincore'])

#%%
#verificamos nombres diferentes de un mes a otro
nombres_diferentes = union[union['nombres y apellidos mes actual'] != \
                           union['nombres y apellidos mes pasado']]
nombres_diferentes = nombres_diferentes[['fincore',
                                         'nombres y apellidos mes actual',
                                         'nombres y apellidos mes pasado'
                                         ]]

#%%
#verificamos los documentos
documento_diferente = union[union['Documento mes pasado'] != \
                            union['Número de Documento 10/']]
documento_diferente = documento_diferente[['fincore',
                                         'Número de Documento 10/',
                                         'Documento mes pasado'
                                         ]]
#%%
#verificamos fecha de nacimiento
nacimiento_diferente = union[union['FechaNacimiento mes pasado'] != \
                            union['Fecha de Nacimiento 3/']]
nacimiento_diferente = nacimiento_diferente[['fincore',
                                         'Fecha de Nacimiento 3/',
                                         'FechaNacimiento mes pasado'
                                         ]]

#%%
#verificamos días de mora > 31 días:
union['dif días de mora'] = union['Dias de Mora 33/'] - \
                            union['DíasMora mes pasado']

dias_mora = union[union['dif días de mora'] > 31]
dias_mora = dias_mora[['fincore',
                       'Dias de Mora 33/',
                       'DíasMora mes pasado',
                       'dif días de mora']]

#%%
union['dif clasificacion'] = union['Clasificación del Deudor con Alineamiento 15/'] - \
                             union['Clasificación Alineamiento mes pasado']

dif_clasificacion = union[(union['dif clasificacion'] < -1) |
                          (union['dif clasificacion'] > 1)]

dif_clasificacion = dif_clasificacion[['fincore',
                                       'Clasificación del Deudor con Alineamiento 15/',
                                       'Clasificación Alineamiento mes pasado']]

#%% concatenamos

x = union[['Nro_Fincore','Clasificación del Deudor con Alineamiento 15/', 
           'Clasificación Alineamiento mes pasado', 'dif clasificacion']]


union.columns

